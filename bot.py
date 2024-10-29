# (©)NextGenBotz

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
    def init(self):  # Change 'init' to 'init'
        super().init(  # Change 'init' to 'init'
            name="Bot",  # Ye 'name' argument yahan rakhne se error resolve hoga
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

        # Handle force subscription channels
        for channel_id in [FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3]:
            if channel_id:
                try:
                    link = (await self.get_chat(channel_id)).invite_link
                    if not link:
                        await self.export_chat_invite_link(channel_id)
                        link = (await self.get_chat(channel_id)).invite_link
                    setattr(self, f'invitelink{len([FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3])}', link)
                except Exception as a:
                    self.LOGGER(name).warning(a)
                    self.LOGGER(name).warning("Bot can't Export Invite link from Force Sub Channel!")
                    self.LOGGER(name).warning(f"Please Double check the channel value and make sure the Bot is Admin with Invite Users via Link Permission.")
                    self.LOGGER(name).info("\nBot Stopped. Join https://t.me/nextgenbotz for support")
                    sys.exit()

        # Check database channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(name).warning(e)
            self.LOGGER(name).warning(f"Make sure the bot is Admin in DB Channel, and double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(name).info("\nBot Stopped. Join https://t.me/nextgenbotz for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(name).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/nextgenbotz")
        self.LOGGER(name).info(""" 
███╗░░██╗███████╗██╗░░██╗████████╗░██████╗░███████╗███╗░░██╗██████╗░░█████╗░████████╗███████╗
████╗░██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝░██╔════╝████╗░██║██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██╔██╗██║█████╗░░░╚███╔╝░░░░██║░░░██║░░██╗░█████╗░░██╔██╗██║██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║╚████║██╔══╝░░░██╔██╗░░░░██║░░░██║░░╚██╗██╔══╝░░██║╚████║██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
██║░╚███║███████╗██╔╝╚██╗░░░██║░░░╚██████╔╝███████╗██║░╚███║██████╦╝╚█████╔╝░░░██║░░░███████╗
╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░╚═════╝░╚══════╝╚═╝░░╚══╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
                                          """)

        self.username = usr_bot_me.username
        
        # Web response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(name).info("Bot stopped.")
