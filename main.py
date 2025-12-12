from telethon import TelegramClient
import asyncio

# Telegram account ma'lumotlari
api_id = 24056411
api_hash = "d235dca2ddb496e8e584e2237afac3e3"
phone = "+998885360310"
session_name = "session_account1"

targets = [
    "@Pubg_chat_mobile_guruh_uzb",
    "@javohir18uzchat",
    "@insta_bozori",
    "@pubg_mobile_chst1",
    "@global_tournament_stars",
    "@halol_admin_uzb",
    "@FC_GURUHH",
    "@Aliycap_chat1",
    "@pubg_chat_mobile_uzbb",
    "@Pubg_Mobile_Chat_Chustlar_Uzb",
    "@REKVZ_24_7",
    "@teotemur_chati","@garand_uzb_forum"
]

message = """BU TARGET YANI OZI AVTO YUBORADI ONLINE BOMASAM HAM SHUNGA LICHGA YOZIB QOYIN OZIM ATVET QILAMAN

ASSALOMU ALAYKUM GRUPPADAGILA PUBG ACCOUNTLA OB QOLAMIZ 20$ DAN 1000$ GACHI KIMDA BOSA BEMALOL YOZVURASILA
----------------------------------------
ACCOUNT XAM SOTAMAN XOXLAGAN ACCOUNTLARIZ BOR NMALA KERELIGINI ETSELA TOPIB BERAMAN 
MUXIMI ISHONCHLI HAMMASI
GURUHGA YOZIB OTIRMELA LICHKAGA YOZILA"""

# Qo'lda event loop yaratish
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient(session_name, api_id, api_hash, loop=loop)

async def main():
    await client.start(phone=phone)
    print("✅ Telegramga muvaffaqiyatli ulanildi!")

    while True:
        for target in targets:
            try:
                await client.send_message(target, message)
                print(f"✅ Xabar yuborildi: {target}")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"❌ Xatolik {target}: {e}")
                await asyncio.sleep(2)

        print("⏳ Hamma guruhlarga xabar yuborildi. 2 minut kutilyapti...")
        await asyncio.sleep(120)

# Botni ishga tushirish
loop.run_until_complete(main())