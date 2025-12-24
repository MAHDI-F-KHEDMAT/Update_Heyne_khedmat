import concurrent.futures
import socket
import time
import re
import requests
import base64

# لیست کامل منابع ارسالی شما
SOURCES = [
    "https://raw.githubusercontent.com/itsyebekhe/PSG/main/subscriptions/xray/base64/mix",
    "https://raw.githubusercontent.com/shaoyouvip/free/refs/heads/main/base64.txt",
    "https://raw.githubusercontent.com/telegeam/freenode/refs/heads/master/v2ray.txt",
    "https://raw.githubusercontent.com/DukeMehdi/FreeList-V2ray-Configs/refs/heads/main/Configs/VLESS-V2Ray-Configs-By-DukeMehdi.txt",
    "https://raw.githubusercontent.com/Flikify/Free-Node/refs/heads/main/v2ray.txt",
    "https://raw.githubusercontent.com/RaitonRed/ConfigsHub/refs/heads/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/shuaidaoya/FreeNodes/refs/heads/main/nodes/base64.txt",
    "https://raw.githubusercontent.com/penhandev/AutoAiVPN/refs/heads/main/allConfigs.txt",
    "https://raw.githubusercontent.com/Firmfox/Proxify/refs/heads/main/v2ray_configs/seperated_by_protocol/vless.txt",
    "https://raw.githubusercontent.com/crackbest/V2ray-Config/refs/heads/main/config.txt",
    "https://raw.githubusercontent.com/kismetpro/NodeSuber/refs/heads/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/jagger235711/V2rayCollector/refs/heads/main/results/vless.txt",
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/refs/heads/main/category/vless.txt",
    "https://raw.githubusercontent.com/SoroushImanian/BlackKnight/refs/heads/main/sub/vless",
    "https://raw.githubusercontent.com/Matin-RK0/ConfigCollector/refs/heads/main/subscription.txt",
    "https://raw.githubusercontent.com/Argh73/VpnConfigCollector/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/3yed-61/configs-collector/refs/heads/main/classified_output/vless.txt",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/refs/heads/main/sub/share/vless",
    "https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/soliSpirit/normal",
    "https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/psgV6/normal",
    "https://raw.githubusercontent.com/ircfspace/XraySubRefiner/refs/heads/main/export/psgMix/normal",
    "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector_Py/refs/heads/main/sub/Mix/mix.txt",
    "https://raw.githubusercontent.com/T3stAcc/V2Ray/refs/heads/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/F0rc3Run/F0rc3Run/refs/heads/main/splitted-by-protocol/vless.txt",
    "https://raw.githubusercontent.com/V2RayRoot/V2RayConfig/refs/heads/main/Config/vless.txt",
    "https://raw.githubusercontent.com/LalatinaHub/Mineral/refs/heads/master/result/nodes",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/hamedcode/port-based-v2ray-configs/refs/heads/main/sub/vless.txt",
    "https://raw.githubusercontent.com/iboxz/free-v2ray-collector/refs/heads/main/main/vless",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/vless.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/vless_configs.txt",
    "https://raw.githubusercontent.com/Pasimand/v2ray-config-agg/refs/heads/main/config.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/vless.html",
    "https://raw.githubusercontent.com/xyfqzy/free-nodes/refs/heads/main/nodes/vless.txt",
    "https://raw.githubusercontent.com/AvenCores/goida-vpn-configs/refs/heads/main/githubmirror/14.txt",
    "https://raw.githubusercontent.com/Awmiroosen/awmirx-v2ray/refs/heads/main/blob/main/v2-sub.txt",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/refs/heads/main/Protocols/vless.txt",
    "https://media.githubusercontent.com/media/gfpcom/free-proxy-list/refs/heads/main/list/vless.txt"
]

OUTPUT_FILE = "sorted_configs.txt"
TIMEOUT = 1.5
MAX_WORKERS = 150 # تعداد ورکر بهینه برای رانر گیتهاب

def is_reality(link):
    """فیلتر اختصاصی پروتکل Reality"""
    return "security=reality" in link.lower()

def fetch_and_decode(url):
    """دانلود و استخراج لینک‌های Reality"""
    links = []
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            content = response.text.strip()
            # اگر محتوا Base64 باشد
            if "vless://" not in content[:50]:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: pass
            
            # استخراج با Regex و فیلتر Reality
            raw_vless = re.findall(r"vless://[^\s]+", content)
            links = [l for l in raw_vless if is_reality(l)]
    except Exception: pass
    return links

def get_address(link):
    """استخراج IP و Port"""
    try:
        match = re.search(r"@([^:/?#]+):(\d+)", link)
        if match:
            return match.group(1), int(match.group(2))
    except: pass
    return None, None

def test_config(link):
    """تست پینگ و پکت‌لاس"""
    ip, port = get_address(link)
    if not ip: return None

    latencies = []
    lost = 0
    rounds = 4

    for _ in range(rounds):
        try:
            start = time.perf_counter()
            # ایجاد یک کانکشن TCP سریع
            sock = socket.create_connection((ip, port), timeout=TIMEOUT)
            latencies.append((time.perf_counter() - start) * 1000)
            sock.close()
        except (socket.timeout, OSError):
            lost += 1
        time.sleep(0.02)

    loss_pct = (lost / rounds) * 100
    if loss_pct == 100: return None # حذف کانفیگ‌های کاملا قطع

    avg_ping = sum(latencies) / len(latencies) if latencies else 9999
    # امتیاز نهایی: پکت لاس وزن بسیار بالایی دارد (1000)
    score = avg_ping + (loss_pct * 1000)
    
    return {"link": link, "score": score}

def main():
    print("--- Starting yekyek Sorter ---")
    all_reality_links = []
    
    # 1. جمع‌آوری اطلاعات از تمام لینک‌ها به صورت همزمان
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as loader:
        results = list(loader.map(fetch_and_decode, SOURCES))
        for r in results:
            all_reality_links.extend(r)
    
    unique_links = list(set(all_reality_links))
    print(f"Total Reality configs found: {len(unique_links)}")

    # 2. تست پایداری و پینگ
    final_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as tester:
        future_to_link = {tester.submit(test_config, l): l for l in unique_links}
        for future in concurrent.futures.as_completed(future_to_link):
            res = future.result()
            if res:
                final_list.append(res)

    # 3. مرتب‌سازی (امتیاز کمتر = کیفیت بهتر)
    sorted_configs = sorted(final_list, key=lambda x: x['score'])

    # 4. ذخیره خروجی نهایی
    with open(OUTPUT_FILE, "w") as f:
        for item in sorted_configs:
            f.write(item['link'] + "\n")

    print(f"Success! {len(sorted_configs)} sorted configs saved in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
