import asyncio
import sys
import io
import time
from flask import Flask, render_template, request, Response, stream_with_context
from youtube_v2 import AdsterraSmartlinkOpener
from playwright.async_api import async_playwright

app = Flask(__name__)

# Stdout capture karne ke liye helper class
class OutputCapture(io.StringIO):
    def __init__(self):
        super().__init__()
        self.new_data = ""
    
    def write(self, data):
        self.new_data += data
        sys.__stdout__.write(data) # Console me bhi dikhaye

    def get_and_clear(self):
        data = self.new_data
        self.new_data = ""
        return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_bot', methods=['POST'])
def run_bot():
    target_link = request.form.get('link')
    user_proxy = request.form.get('proxy')
    
    # Validation
    if not target_link:
        return "Error: Link is required"

    def generate():
        # Output capture start
        capture = OutputCapture()
        original_stdout = sys.stdout
        sys.stdout = capture
        
        yield ">> SYSTEM INITIALIZED...\n"
        yield f">> TARGET: {target_link}\n"
        yield f">> PROXY: {user_proxy if user_proxy else 'Using Random/Default'}\n"
        yield ">> STARTING ENGINE (playwright)...\n\n"

        async def run_single_cycle():
            try:
                # Bot instance create karein
                opener = AdsterraSmartlinkOpener()
                
                # Agar user ne proxy di hai, to bot ki proxy list ko override karein
                if user_proxy:
                    # User ki proxy ko list me dalein taaki wahi select ho
                    opener.proxy_credentials = [user_proxy] 
                    # Note: Agar full proxy url (http://...) hai to script shayad adjust kare,
                    # par hum assume kar rahe hain tumhara script format handle kar lega.

                async with async_playwright() as p:
                    # Browser Launch
                    browser = await p.chromium.launch(
                        headless=True, # Web server par headless hi chalega
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-dev-shm-usage"
                        ]
                    )
                    
                    yield ">> BROWSER LAUNCHED. CREATING CONTEXT...\n"
                    
                    # Single link process karein (Random profile ke saath)
                    # Hum tumhare script ka internal function use karenge
                    success = await opener._open_smartlink_with_random_profile(browser, target_link, link_index=1)
                    
                    if success:
                        yield "\n>> [SUCCESS] OPERATION COMPLETED SUCCESSFULLY.\n"
                    else:
                        yield "\n>> [FAILED] OPERATION ENCOUNTERED ERRORS.\n"
                        
                    await browser.close()
                    yield ">> BROWSER CLOSED.\n"
                    
            except Exception as e:
                yield f"\n>> [CRITICAL ERROR]: {str(e)}\n"

        # Async loop ko sync generator me chalana
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Background me task run karein aur output stream karein
        task = loop.create_task(run_single_cycle())
        
        while not task.done():
            # Check for new logs
            logs = capture.get_and_clear()
            if logs:
                yield logs
            time.sleep(0.1)
            
            # Agar task abhi bhi chal raha hai to thoda wait
            loop.run_until_complete(asyncio.sleep(0.1))
        
        # Final logs
        yield capture.get_and_clear()
        
        # Restore stdout
        sys.stdout = original_stdout
        yield "\n>> PROCESS TERMINATED."

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
      
