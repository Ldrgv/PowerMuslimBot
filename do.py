''' Run a function by ado <func_name> '''


def set_hook():
    import asyncio
    from bot.config import HEROKU_APP_NAME, WEBHOOK_URL, BOT_TOKEN
    from aiogram import Bot
    bot = Bot(token=BOT_TOKEN)

    async def hook_set():
        await bot.set_webhook(WEBHOOK_URL)
        print(await bot.get_webhook_info())
    

    asyncio.run(hook_set())
    bot.close()


if __name__=="__main__":
    from bot.bot import main
    main()