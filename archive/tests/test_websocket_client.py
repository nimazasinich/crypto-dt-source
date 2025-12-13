#!/usr/bin/env python3
"""
تست WebSocket Client
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    uri = "ws://localhost:7860/ws"
    
    print("=" * 80)
    print("🧪 تست WebSocket Client")
    print("=" * 80)
    print(f"\n🔌 اتصال به: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ اتصال برقرار شد!")
            
            # دریافت پیام اولیه
            print("\n📨 در حال دریافت پیام اولیه...")
            message = await websocket.recv()
            data = json.loads(message)
            
            print(f"\n✅ پیام اولیه دریافت شد:")
            print(f"   Type: {data.get('type')}")
            print(f"   Total Resources: {data.get('data', {}).get('total_resources')}")
            print(f"   Categories: {data.get('data', {}).get('total_categories')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            
            # ارسال ping به سرور
            print("\n📤 ارسال ping به سرور...")
            await websocket.send("ping")
            print("✅ پیام ارسال شد")
            
            # دریافت پاسخ
            print("\n📨 در انتظار پاسخ...")
            response = await websocket.recv()
            pong_data = json.loads(response)
            
            print(f"\n✅ پاسخ دریافت شد:")
            print(f"   Type: {pong_data.get('type')}")
            print(f"   Message: {pong_data.get('message')}")
            print(f"   Timestamp: {pong_data.get('timestamp')}")
            
            # صبر برای دریافت بروزرسانی‌های دوره‌ای
            print("\n⏳ صبر برای بروزرسانی دوره‌ای (10 ثانیه)...")
            
            try:
                update = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                update_data = json.loads(update)
                
                print(f"\n✅ بروزرسانی دریافت شد:")
                print(f"   Type: {update_data.get('type')}")
                print(f"   Data: {json.dumps(update_data.get('data'), indent=2)}")
                
            except asyncio.TimeoutError:
                print("\n⚠️  Timeout - بروزرسانی دریافت نشد (طبیعی است)")
            
            print("\n" + "=" * 80)
            print("✅ تست WebSocket با موفقیت کامل شد!")
            print("=" * 80)
            
    except ConnectionRefusedError:
        print("\n❌ خطا: سرور در دسترس نیست!")
        print("لطفاً ابتدا سرور را راه‌اندازی کنید:")
        print("   python3 app.py")
    except Exception as e:
        print(f"\n❌ خطا: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
