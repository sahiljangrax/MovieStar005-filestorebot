# bot.py

from aiohttp import web
from plugins import web_server

import pyromod.listen
import pyrogram
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, CHANNEL_ID, PORT

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999

class Bot(Client):
    def init(self):
        super().init(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        try:
            # Handling Force Subscriptions
            if FORCE_SUB_CHANNEL:
                self.invitelink = await self._export_chat_invite(FORCE_SUB_CHANNEL)
            if FORCE_SUB_CHANNEL2:
                self.invitelink2 = await self._export_chat_invite(FORCE_SUB_CHANNEL2)
            if FORCE_SUB_CHANNEL3:
                self.invitelink3 = await self._export_chat_invite(FORCE_SUB_CHANNEL3)

            # DB Channel and Test Message
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()

        except Exception as e:
            self.LOGGER.warning(e)
            self.LOGGER.warning("Make sure bot is Admin in DB Channel and check CHANNEL_ID value.")
            self.LOGGER.info("Bot Stopped. Join https://t.me/nextgenbotz for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER.info("Bot Running..!\nCreated by https://t.me/nextgenbotz")
        self.LOGGER.info("""
        ███╗░░██╗███████╗██╗░░██╗████████╗░██████╗░███████╗███╗░░██╗██████╗░░█████╗░████████╗███████╗
        ████╗░██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝░██╔════╝████╗░██║██╔══██╗██╔══██╗╚══██╔══╝╚════██║
        ██╔██╗██║█████╗░░░╚███╔╝░░░░██║░░░██║░░██╗░█████╗░░██╔██╗██║██████╦╝██║░░██║░░░██║░░░░░███╔═╝
        ██║╚████║██╔══╝░░░██╔██╗░░░░██║░░░██║░░╚██╗██╔══╝░░██║╚████║██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
        ██║░╚███║███████╗██╔╝╚██╗░░░██║░░░╚██████╔╝███████╗██║░╚███║██████╦╝╚█████╔╝░░░██║░░░███████╗
        ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░╚═════╝░╚══════╝╚═╝░░╚══╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
        """)
        self.username = usr_bot_me.username

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER.info("Bot stopped.")

    async def _export_chat_invite(self, channel_id):
        try:
            link = (await self.get_chat(channel_id)).invite_link
            if not link:
                await self.export_chat_invite_link(channel_id)
                link = (await self.get_chat(channel_id)).invite_link
            return link
        except Exception as e:
            self.LOGGER.warning(e)
            self.LOGGER.warning(f"Bot can't Export Invite link for channel ID: {channel_id}. Make sure the bot has admin permissions.")
            sys.exit()
