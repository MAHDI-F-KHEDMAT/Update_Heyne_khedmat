import concurrent.futures
import socket
import time
import re
import requests
import base64

# لیست کامل منابع ارسالی شما
SOURCES = [
    "https://raw.githubusercontent.com/itsyebekhe/PSG/main/subscriptions/xray/base64/mix",
    "https://raw.githubusercontent.com/R3ZARAHIMI/tg-v2ray-configs-every2h/refs/heads/main/conf-week.txt",
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/refs/heads/main/githubmirror/new/all_new.txt",
    "https://raw.githubusercontent.com/shuaidaoya/FreeNodes/refs/heads/main/nodes/base64.txt",
    "https://raw.githubusercontent.com/Flikify/Free-Node/refs/heads/main/v2ray.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/refs/heads/master/v2ray",
    "https://raw.githubusercontent.com/w154594742/free-v2ray-node/refs/heads/master/v2ray.txt",
    "https://raw.githubusercontent.com/w154594742/freeNode/refs/heads/main/all.txt",
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
MAX_WORKERS = 250 # بهینه شده برای GitHub Actions

def is_reality(link):
    """فیلتر اختصاصی برای جدا کردن پروتکل Reality"""
    return "security=reality" in link.lower()

def smart_deduplicate(links):
    """حذف تکراری‌ها بر اساس آدرس و UUID، نادیده گرفتن نام سرور"""
    unique_configs = {}
    for link in links:
        # حذف نام سرور بعد از علامت #
        tech_part = link.split('#')[0]
        if tech_part not in unique_configs:
            unique_configs[tech_part] = link
    return list(unique_configs.values())

def fetch_and_decode(url):
    """دانلود و رمزگشایی لینک‌ها از منابع"""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            content = response.text.strip()
            # اگر محتوا احتمالاً Base64 باشد (فاقد پروتکل مستقیم)
            if "vless://" not in content[:50]:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: pass
            
            raw_vless = re.findall(r"vless://[^\s]+", content)
            # فیلتر کردن فقط Realityها در مرحله استخراج
            return [l for l in raw_vless if is_reality(l)]
    except: pass
    return []

def test_config(link):
    """تست پینگ و پکت‌لاس در 4 مرحله"""
    match = re.search(r"@([^:/?#]+):(\d+)", link)
    if not match: return None
    ip, port = match.group(1), int(match.group(2))

    latencies, lost = [], 0
    for _ in range(4):
        try:
            start = time.perf_counter()
            with socket.create_connection((ip, port), timeout=TIMEOUT) as sock:
                latencies.append((time.perf_counter() - start) * 1000)
        except:
            lost += 1
        time.sleep(0.01)

    loss_pct = (lost / 4) * 100
    if loss_pct == 100: return None # حذف سرورهای کاملاً خاموش

    avg_ping = sum(latencies) / len(latencies) if latencies else 9999
    # امتیاز: اولویت با پایداری (پکت‌لاس صفر) و سپس سرعت (پینگ کمتر)
    score = avg_ping + (loss_pct * 1000)
    return {"link": link, "score": score}

def main():
    start_all = time.time()
    print("🚀 [1/4] Harvesting Reality configs from sources...")
    
    all_raw_reality = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as loader:
        results = list(loader.map(fetch_and_decode, SOURCES))
        for r in results: all_raw_reality.extend(r)
    
    print(f"📦 Total Reality links found: {len(all_raw_reality)}")

    print("🔍 [2/4] Executing Smart Deduplication...")
    unique_links = smart_deduplicate(all_raw_reality)
    print(f"💎 Unique configs to test: {len(unique_links)} (Removed {len(all_raw_reality)-len(unique_links)} duplicates)")

    print(f"⚡ [3/4] Testing {len(unique_links)} configs with {MAX_WORKERS} workers...")
    
    final_list = []
    tested = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as tester:
        futures = {tester.submit(test_config, l): l for l in unique_links}
        for f in concurrent.futures.as_completed(futures):
            tested += 1
            res = f.result()
            if res: final_list.append(res)
            
            # چاپ گزارش زنده هر 100 تست
            if tested % 100 == 0 or tested == len(unique_links):
                print(f"⏱️ Progress: {tested}/{len(unique_links)} | Found {len(final_list)} alive")

    print("📊 [4/4] Ranking and Saving results...")
    # مرتب‌سازی بر اساس امتیاز (کمترین امتیاز بهترین است)
    sorted_configs = sorted(final_list, key=lambda x: x['score'])

    with open(OUTPUT_FILE, "w") as f:
        for item in sorted_configs:
            f.write(item['link'] + "\n")

    end_all = time.time()
    print(f"✅ [FINISHED] Process completed in {round(end_all - start_all, 2)} seconds.")
    print(f"🏆 Best configs are at the top of '{OUTPUT_FILE}'. Total healthy: {len(final_list)}")

if __name__ == "__main__":
    main()
