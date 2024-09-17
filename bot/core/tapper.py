import asyncio
import inspect
import hmac
import hashlib
import pprint
import random
from urllib.parse import unquote
from time import time
from datetime import datetime

import aiohttp
import json
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.random_sleep = random.randint(*settings.SLEEP_RANDOM)

    async def get_secret(self, userid):
        key_hash = str("adwawdasfajfklasjglrejnoierjboivrevioreboidwa").encode('utf-8')
        message = str(userid).encode('utf-8')
        hmac_obj = hmac.new(key_hash, message, hashlib.sha256)
        secret = str(hmac_obj.hexdigest())
        return secret

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('true_coin_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://bot.true.world/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            self.user_id = (await self.tg_client.get_me()).id
            self.username = ''

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=30)


    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")
            await asyncio.sleep(delay=30)

    async def login(self, http_client: aiohttp.ClientSession):
        try:
            current_time = datetime.utcnow()
            formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            http_client.headers["sendtime"] = f"{formatted_time}"

            url = 'https://api.true.world/api/auth/signIn'
            data = {'lang': 'ru', 'userId': self.user_id}
            logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}], data: [{data}]")
            await asyncio.sleep(delay=self.random_sleep)
            response = await http_client.post(url=url, json=data)

            if response.ok:
                response_json = await response.json()
                return response_json
            else:
                return False

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when login: {error} ")
            await asyncio.sleep(delay=30)

    async def api(self, http_client: aiohttp.ClientSession, action='', api_id: int = 0):
        try:
            sleep_spins = random.randint(*settings.SLEEP_BETWEEN_SPINS)
            current_time = datetime.utcnow()
            formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            http_client.headers["sendtime"] = f"{formatted_time}"
            await asyncio.sleep(delay=sleep_spins)

            match action:
                case 'getCurrentSpins':
                    url = f"https://api.true.world/api/game/{action}"
                    logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}], "
                                f"action [{action}]")
                    response = await http_client.get(url=url)
                    response.raise_for_status()
                    if response.ok:
                        response_json = await response.json()
                        return response_json
                    else:
                        response_json = {}
                        return response_json

                case 'spin':
                    url = f"https://api.true.world/api/game/{action}"
                    logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}], "
                                f"action [{action}]")
                    response = await http_client.get(url=url)
                    response.raise_for_status()
                    if response.ok:
                        response_json = await response.json()
                        return response_json
                    else:
                        response_json = {}
                        return response_json

                case 'getLastReward':
                    url = f"https://api.true.world/api/dailyReward/{action}"
                    logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}], "
                                f"action [{action}]")
                    response = await http_client.get(url=url)
                    response.raise_for_status()
                    if response.ok:
                        response_json = await response.json()
                        return response_json
                    else:
                        response_json = {}
                        return response_json

                case 'collectReward':
                    url = f"https://api.true.world/api/dailyReward/{action}"
                    logger.info(f"{self.session_name} | bot action: [{inspect.currentframe().f_code.co_name}], "
                                f"action [{action}]")
                    response = await http_client.get(url=url)
                    response.raise_for_status()
                    if response.ok:
                        response_json = await response.json()
                        return response_json
                    else:
                        response_json = {}
                        return response_json

                case _:
                    logger.error(f"{self.session_name} | ERROR API | no api action ")

        except Exception as error:
            logger.error(f"{self.session_name} | API Unknown error: {error}")
            await asyncio.sleep(delay=10)

    async def run(self, proxy: str | None) -> None:
        while True:
            try:
                #
                random_sleep = random.randint(*settings.SLEEP_RANDOM)
                mining_sleep = random.randint(*settings.SLEEP_BETWEEN_MINING)

                http_client = CloudflareScraper(headers=headers)
                http_client.headers["auth-key"] = settings.API_KEY
                tg_web_data = await self.get_tg_web_data(proxy=proxy)

                login_data = await self.login(http_client=http_client)
                access_token = login_data.get('token')
                logger.info(f"Generate new access_token: {access_token[:64]}")
                http_client.headers["authorization"] = f"Bearer {access_token}"

                login_username = login_data['user'].get('username')
                login_coins = login_data['user'].get('coins')
                login_currentSpins = login_data['user'].get('currentSpins')
                login_maxSpins = login_data['user'].get('maxSpins')

                logger.success(f"{self.session_name} "
                               f"Username: <c>{login_username}</c>, Coins: <c>{login_coins}</c> | "
                               f"Spins: <e>{login_currentSpins}/{login_maxSpins}</e> ")

                if settings.APPLY_DAILY_REWARD:
                    action = 'getLastReward'
                    api_data = await self.api(http_client=http_client, action=action)
                    logger.success(f"{self.session_name} | Bot action: <red>[api/{action}]</red> : <c>{api_data}</c>")
                    collectReward = False

                    if api_data == {}:
                        collectReward = True
                    else:
                        date_from_str = datetime.strptime(api_data['createdDate'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                        current_date = datetime.utcnow().date()
                        if date_from_str != current_date:
                            collectReward = True

                    if collectReward:
                        action = 'collectReward'
                        api_data = await self.api(http_client=http_client, action=action)
                        if api_data:
                            logger.success(
                                f"{self.session_name} | Bot action: <red>[api/{action}]</red> : <c>{api_data}</c>")
                        else:
                            logger.error(
                                f"{self.session_name} | Bot action: <red>[api/{action}]</red> : <c>{api_data}</c>")

                if settings.AUTO_SPIN:
                    action = 'getCurrentSpins'
                    api_data = await self.api(http_client=http_client, action=action)
                    if api_data:
                        logger.success(f"{self.session_name} | Bot action: <red>[api/{action}]</red> : <c>{api_data}</c>")
                        currentSpins = int(api_data.get('currentSpins'))
                    else:
                        currentSpins = 0

                    while currentSpins > 0:
                        action = 'spin'
                        api_data = await self.api(http_client=http_client, action=action)
                        if api_data:
                            logger.success(
                                f"{self.session_name} | Bot action: <red>[api/{action}/{currentSpins}]</red> : "
                                f"<c>{api_data['result']}</c>")
                            currentSpins = int(api_data['user'].get('currentSpins'))
                        else:
                            currentSpins = 0

                if settings.SPINS_DAILY_AD:
                    boosts = login_data['boosts']
                    for boost in boosts:
                        if boost['cost'] == 0:
                            print(boost)


                #         random_sleep = random.randint(*settings.SLEEP_RANDOM)
                #
                #         if not mission.get('status'):
                #             task_action = 'startMission'
                #             logger.info(f"{self.session_name} | Sleep {random_sleep:,}s before: <g>[task/{task_action}/{mission['id']}]:</g> <c>{mission['name']}</c>")
                #             mission_data = await self.api(http_client=http_client, api_action=task_action, api_id=mission['id'])
                #             if mission_data:
                #                 logger.success(f"{self.session_name} | Bot action: <red>[task/{task_action}/{mission['id']}]</red> : <c>{mission_data}</c>")
                #             await asyncio.sleep(delay=random_sleep)
                #
                #             for task in mission['tasks']:
                #                 task_action = 'startTask'
                #                 logger.info(f"{self.session_name} | Sleep {random_sleep:,}s before: <g>[task/{task_action}/{task['id']}]:</g> <c>{task['name']}</c>")
                #                 task_data = await self.api(http_client=http_client, api_action=task_action, api_id=task['id'])
                #                 if task_data:
                #                     logger.success(
                #                         f"{self.session_name} | Bot action: <red>[task/{task_action}/{mission['id']}]</red> : <c>{task_data}</c>")
                #                 await asyncio.sleep(delay=random_sleep)
                #         else:
                #             for task in mission['tasks']:
                #                 if task['status'] != 3 and task['id'] not in self.skip_tasks_id:
                #                     task_action = 'checkTask'
                #                     logger.info(f"{self.session_name} | Sleep {random_sleep:,}s before: <g>[task/{task_action}/{task['id']}]:</g> <c>{task['name']}</c>")
                #                     task_data = await self.api(http_client=http_client, api_action=task_action, api_id=task['id'])
                #
                #                     #if task_data and task_data.get('status') == 'wait':
                #                     if task_data:
                #                         logger.success(f"{self.session_name} | Bot action: <red>[task/{task_action}/{mission['id']}]</red> : <c>{task_data}</c>")
                #                         for tasks in tasks_data:
                #                             if tasks['id'] == task['id']:
                #                                 task['time'] = int(time())
                #                                 found = True
                #                                 break
                #                         if not found:
                #                             tasks_data.append({'id': task['id'], 'time': int(time())})
                #                         logger.info(f"{self.session_name} | <g>[task/{task_action}/{task['id']}]:</g> <c>{found}</c>")
                #                     else:
                #                         for tasks in tasks_data:
                #                             if tasks['id'] == task['id']:
                #                                 task['time'] = int(time())
                #                                 found = True
                #                                 break
                #                         if not found:
                #                             tasks_data.append({'id': task['id'], 'time': int(time())})
                #                         logger.info(
                #                             f"{self.session_name} | <g>[task/{task_action}/{task['id']}]:</g> <c>{found}</c>")
                #                     await asyncio.sleep(delay=random_sleep)
                #
                # for tasks_data_id in tasks_data:
                #     if (time() - tasks_data_id['time'] > 3600*8) and (tasks_data_id['id'] in self.skip_tasks_id):
                #         print('TIMEOUT:REMOVE', tasks_data_id['id'], tasks_data_id['time'])
                #         self.skip_tasks_id.remove(tasks_data_id['id'])
                #     else:
                #         if tasks_data_id['id'] not in self.skip_tasks_id:
                #             print('TIMEOUT:ADD', tasks_data_id['id'], tasks_data_id['time'])
                #             self.skip_tasks_id.append(tasks_data_id['id'])
                #         else:
                #             print('TIMEOUT:LIST', tasks_data_id['id'], tasks_data_id['time'])
                #
                #     #print(self.skip_tasks_id)
                #     #print(tasks_data)
                #
                # if settings.AUTO_TAP:
                #     while topcoinbot_energy > settings.MIN_AVAILABLE_ENERGY:
                #         taps = random.randint(*settings.RANDOM_TAPS_COUNT)
                #         tap_sleep = random.randint(*settings.SLEEP_BETWEEN_TAP)
                #
                #         status_options = await self.task_tap_options(http_client=http_client_options)
                #         if status_options: print("Tap Options sent successfully")
                #
                #         task_data = await self.task_tap(http_client=http_client, taps=taps)
                #
                #         topcoinbot_balance = task_data['balance']
                #         status_calc_taps = taps * topcoinbot_multitap
                #         topcoinbot_energy = task_data['energy']
                #         topcoinbot_score = task_data['score']
                #
                #         logger.success(f"{self.session_name} | bot action: <red>[tap/{taps}]</red> | "
                #                f"Balance: <c>{topcoinbot_balance:,}</c> (<g>+{status_calc_taps}</g>), Energy: <e>{topcoinbot_energy}</e>, Score: <e>{topcoinbot_score:,}</e> "
                #                f"Sleep: {tap_sleep}s")
                #         await asyncio.sleep(delay=tap_sleep)
                #
                #         if (topcoinbot_boost_fullTankLeft > 0
                #                 and time() - topcoinbot_boost_fullTankLeft_time >= 1800
                #                 and topcoinbot_energy < settings.MIN_AVAILABLE_ENERGY
                #                 and settings.APPLY_DAILY_ENERGY is True):
                #             logger.info(f"{self.session_name} | Sleep 5s before activating the daily energy boost")
                #             await asyncio.sleep(delay=5)
                #
                #             statusboost: bool = await self.apply_boost_fullTank(http_client=http_client)
                #             if statusboost is True:
                #                 logger.success(f"{self.session_name} | Energy boost applied")
                #                 topcoinbot_energy += 1000
                #                 topcoinbot_boost_fullTankLeft_time = time()
                #                 await asyncio.sleep(delay=1)
                #             continue
                #
                #         if (topcoinbot_boost_tappingGuruLeft > 0
                #                 and time() - topcoinbot_boost_tappingGuruLeft_time >= 1800
                #                 and settings.APPLY_DAILY_TURBO is True):
                #             logger.info(f"{self.session_name} | Sleep 5s before activating the daily turbo boost")
                #             await asyncio.sleep(delay=5)
                #
                #             statusboost: bool = await self.apply_boost_tappingGuruLeft(http_client=http_client)
                #             if statusboost is True:
                #                 logger.success(f"{self.session_name} | Turbo boost applied")
                #                 await asyncio.sleep(delay=1)
                #                 topcoinbot_boost_tappingGuruLeft_time = time()
                #             continue
                #     else:
                #         taps = abs(topcoinbot_energy // topcoinbot_multitap - 1)
                #         status_options = await self.task_tap_options(http_client=http_client_options)
                #         if status_options: print("Tap Options sent successfully")
                #         task_data = await self.task_tap(http_client=http_client, taps=taps)
                #
                #         topcoinbot_balance = task_data['balance']
                #         status_calc_taps = taps * topcoinbot_multitap
                #         topcoinbot_energy = task_data['energy']
                #         topcoinbot_score = task_data['score']
                #         logger.success(f"{self.session_name} | bot action: <red>[tap/{taps}]</red> | "
                #                f"Balance: <c>{topcoinbot_balance:,}</c> (<g>+{status_calc_taps}</g>), Energy: <e>{topcoinbot_energy:,}</e>, Score: <e>{topcoinbot_score:,}</e>")

                #Final SLEEP
                logger.info(f"{self.session_name} | Minimum spins reached. Sleep {mining_sleep:,}s")
                await http_client.close()
                await asyncio.sleep(delay=mining_sleep)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await http_client.close()
                await asyncio.sleep(delay=300)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")

