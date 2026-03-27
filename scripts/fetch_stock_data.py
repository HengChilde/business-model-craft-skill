#!/usr/bin/env python3
"""
business-model-craft-skill 自动选股脚本
目标：选出市场上正在引起关注的公司，为分析内容提供更好的 SEO 表现
策略：多源实时查询（Google Finance 为主力）+ StockAnalysis 补充 + 固定候选池兜底
       Alpha Vantage API 为最低优先级（需用户自行配置 API Key）

Alpha Vantage API Key 说明：
  免费申请地址：https://www.alphavantage.co
  点击页面上的 "Get your free API key today"，填写邮箱即可（无需信用卡）
  免费版：每分钟 5 次请求、每天 25 次
  配置方式（二选一）：
    方法 A（推荐）：export ALPHA_VANTAGE_API_KEY="your_key_here"
    方法 B：修改本文件中的 ALPHA_VANTAGE_API_KEY 变量
"""

import os
import sys
import json
import random
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path

# ─────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────

# Alpha Vantage API Key：需用户自行申请
# 申请地址：https://www.alphavantage.co → "Get your free API key today" → 填邮箱即可
# 优先从环境变量读取；未配置时保持空字符串，脚本将跳过 Alpha Vantage 数据源
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
MIN_MARKET_CAP = 1_000_000_000  # $10 亿最低市值
TARGET_RESULTS = 3              # 最终返回候选数量
AV_MAX_CALLS = 5               # AV OVERVIEW 最多调用次数

# 不值得分析商业模式的标的（ETF、杠杆基金等）
KNOWN_UNSUITABLE = {
    "SPY", "QQQ", "IWM", "DIA", "GLD", "SLV", "TLT", "HYG", "LQD",
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLB", "XLC", "XLU", "XLP", "XLY",
    "ARKK", "ARKG", "ARKF", "ARKQ", "ARKW",
    "VTI", "VOO", "VGT", "VNQ", "VXUS", "SCHD", "JEPI",
    "TZA", "TNA", "SPXU", "SPXS", "SQQQ", "TQQQ", "UVXY", "SVXY",
    "LABD", "LABU", "JNUG", "JDST", "NUGT", "DUST",
    "SOXS", "SOXL", "TECL", "TECS", "FNGU", "FNGD",
    "IBIT", "BITO", "GBTC",  # 比特币 ETF
}

# 已知为 ETF 的名称关键词
ETF_NAME_KEYWORDS = ["ETF", "TRUST", "FUND", "INDEX", "ISHARES", "VANGUARD",
                     "SPDR", "INVESCO", "DIREXION", "PROSHARES"]

OUTPUT_DIR_ENV_KEYS = ("BUSINESSMODELCRAFT_OUTPUT_BASE", "BUSINESSMODELCRAFT_OUTPUT_DIR")
OUTPUT_FOLDER_NAME = "BusinessModelCraft"


def resolve_output_root() -> Path:
    """解析四件套产出根目录。"""
    for env_key in OUTPUT_DIR_ENV_KEYS:
        raw_value = os.getenv(env_key, "").strip()
        if not raw_value:
            continue
        candidate = Path(raw_value).expanduser()
        if candidate.name == OUTPUT_FOLDER_NAME:
            return candidate
        return candidate / OUTPUT_FOLDER_NAME
    return Path.home() / "Documents" / OUTPUT_FOLDER_NAME


def is_likely_etf_or_fund(symbol, name=""):
    """快速判断是否为 ETF / 基金 / 不适合分析的标的"""
    sym = symbol.upper()
    if sym in KNOWN_UNSUITABLE:
        return True
    # 认股权证/Unit/Rights 后缀
    if len(sym) > 4 and sym.endswith(("W", "R")):
        return True
    # 名称中包含 ETF 关键词
    if name:
        name_upper = name.upper()
        for kw in ETF_NAME_KEYWORDS:
            if kw in name_upper:
                return True
    return False


# ─────────────────────────────────────────────
# 本地 / 网站去重
# ─────────────────────────────────────────────

def get_local_analyzed(output_dir):
    """扫描本地输出目录，返回 (slugs_set, symbols_set)"""
    slugs, symbols = set(), set()
    if not os.path.exists(output_dir):
        return slugs, symbols
    try:
        for entry in os.listdir(output_dir):
            full_path = os.path.join(output_dir, entry)
            if not os.path.isdir(full_path):
                continue
            for filename in os.listdir(full_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(full_path, filename), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data.get("slug"):
                                slugs.add(data["slug"].lower())
                            if data.get("symbol"):
                                symbols.add(data["symbol"].upper())
                    except Exception:
                        pass
    except Exception as e:
        print(f"Warning: 扫描本地目录出错: {e}", file=sys.stderr)
    return slugs, symbols


def get_published_slugs():
    """抓取 businessmodelcraft.com 已发布的 slug 列表"""
    published = set()
    try:
        url = "https://businessmodelcraft.com/en/examples"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        published.update(re.findall(r'/en/examples/([a-z0-9\-]+)', html))
    except Exception as e:
        print(f"Warning: 无法抓取网站已发布列表: {e}", file=sys.stderr)
    return published


# ─────────────────────────────────────────────
# 数据源 1: Google Finance（主力）
# ─────────────────────────────────────────────

def source_google_finance():
    """
    抓取 Google Finance 热门页面。
    Google Finance 的服务端 HTML 只预渲染少量数据（通常 5-6 条），
    但这些都是当日真正在市场上引起关注的公司，质量高、SEO 价值强。
    """
    print("📡 [Source 1] Google Finance...", file=sys.stderr)

    pages = [
        ("https://www.google.com/finance/markets/gainers",    "Top Gainer"),
        ("https://www.google.com/finance/markets/losers",     "Top Loser"),
        ("https://www.google.com/finance/markets/most-active","Most Active"),
    ]

    candidates = []
    seen = set()

    for url, label in pages:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html",
            })
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # 匹配格式：href="./quote/SYMBOL:EXCHANGE" title="Company Name"
            matches = re.findall(
                r'href=["\']\.\/quote\/([A-Z]{1,5}):(NYSE|NASDAQ|NYSEARCA|NYSEMKT|AMEX)["\'][^>]*title=["\']([^"\']+)["\']',
                html
            )

            count = 0
            for sym, exchange, company_name in matches:
                if sym in seen:
                    continue
                if is_likely_etf_or_fund(sym, company_name):
                    continue
                seen.add(sym)
                candidates.append({
                    "symbol": sym,
                    "name": company_name,
                    "source": "google_finance",
                    "reason": label,
                    "exchange": exchange,
                })
                count += 1

            if count > 0:
                print(f"  [{label}] {count} 个", file=sys.stderr)

        except Exception as e:
            print(f"  ⚠️ {url} 失败: {e}", file=sys.stderr)
            continue

    print(f"  ✅ 共获取 {len(candidates)} 个候选", file=sys.stderr)
    return candidates

    print(f"  ✅ 获取 {len(candidates)} 个候选", file=sys.stderr)
    return candidates


# ─────────────────────────────────────────────
# 数据源 2: Alpha Vantage TOP_GAINERS_LOSERS
# ─────────────────────────────────────────────

def source_alpha_vantage():
    """从 Alpha Vantage 获取当日市场热门股票（最低优先级，需配置 API Key）"""
    if not ALPHA_VANTAGE_API_KEY:
        print("📡 [Source AV] Alpha Vantage 跳过（未配置 API Key）", file=sys.stderr)
        print("   申请地址：https://www.alphavantage.co → \"Get your free API key today\"", file=sys.stderr)
        return []
    print("📡 [Source AV] Alpha Vantage...", file=sys.stderr)
    try:
        url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={ALPHA_VANTAGE_API_KEY}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        if "Note" in data or "Information" in data:
            print("  ⚠️ API 限频", file=sys.stderr)
            return []
        if "Error Message" in data:
            print(f"  ⚠️ API 错误", file=sys.stderr)
            return []

        candidates = []
        seen = set()
        for category in ["top_gainers", "top_losers", "most_actively_traded"]:
            for item in data.get(category, []):
                ticker = item.get("ticker", "")
                if not ticker or ticker in seen:
                    continue
                try:
                    price = float(item.get("price", "0"))
                    volume = int(item.get("volume", "0"))
                except (ValueError, TypeError):
                    continue
                if price < 3.0 or volume < 500_000:
                    continue
                if is_likely_etf_or_fund(ticker):
                    continue
                seen.add(ticker)
                candidates.append({
                    "symbol": ticker,
                    "name": "",
                    "source": "alpha_vantage",
                    "reason": category.replace("_", " ").title(),
                    "price": price,
                    "volume": volume,
                })

        print(f"  ✅ 获取 {len(candidates)} 个候选", file=sys.stderr)
        return candidates

    except Exception as e:
        print(f"  ❌ 失败: {e}", file=sys.stderr)
        return []


# ─────────────────────────────────────────────
# 数据源 3: StockAnalysis 热门页面
# ─────────────────────────────────────────────

def source_stockanalysis():
    """抓取 StockAnalysis Gainers/Losers/Active，只取白名单候选"""
    print("📡 [Source 3] StockAnalysis...", file=sys.stderr)
    pages = [
        ("https://stockanalysis.com/markets/gainers/", "Top Gainer"),
        ("https://stockanalysis.com/markets/losers/",  "Top Loser"),
        ("https://stockanalysis.com/markets/active/",  "Most Active"),
    ]
    candidates = []
    seen = set()
    for url, label in pages:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html",
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            # 精准匹配表格中直接链接的股票代码
            syms = re.findall(r'href=["\']\/stocks\/([A-Za-z]{1,5})["\/ ]', html)
            count = 0
            for sym in syms:
                sym = sym.upper()
                if sym in seen or not (1 < len(sym) <= 5):
                    continue
                if sym in {"ETF", "IPO", "PRO", "LIST", "NEWS", "LOG", "FAQ", "MAP"}:
                    continue
                if is_likely_etf_or_fund(sym):
                    continue
                seen.add(sym)
                candidates.append({
                    "symbol": sym, "name": "",
                    "source": "stockanalysis", "reason": label,
                })
                count += 1
                if count >= 15:
                    break
        except Exception as e:
            print(f"  ⚠️ {url}: {e}", file=sys.stderr)

    print(f"  ✅ 获取 {len(candidates)} 个候选", file=sys.stderr)
    return candidates


# ─────────────────────────────────────────────
# 数据源 4: 固定候选池（真正最后兜底）
# ─────────────────────────────────────────────

FALLBACK_POOL = [
    # 消费科技 / 平台
    ("AAPL","Apple"), ("AMZN","Amazon"), ("NFLX","Netflix"),
    ("SPOT","Spotify"), ("SNAP","Snap"), ("PINS","Pinterest"),
    ("DUOL","Duolingo"), ("RBLX","Roblox"), ("MTCH","Match Group"),
    # SaaS
    ("CRM","Salesforce"), ("NOW","ServiceNow"), ("SNOW","Snowflake"),
    ("DDOG","Datadog"), ("ZS","Zscaler"), ("CRWD","CrowdStrike"),
    ("HUBS","HubSpot"), ("TEAM","Atlassian"), ("MDB","MongoDB"),
    ("NET","Cloudflare"), ("GTLB","GitLab"),
    # AI / 半导体
    ("AMD","AMD"), ("INTC","Intel"), ("AVGO","Broadcom"),
    ("ASML","ASML"), ("TSM","TSMC"),
    # 金融科技
    ("V","Visa"), ("MA","Mastercard"), ("SQ","Block"),
    ("PYPL","PayPal"), ("AFRM","Affirm"), ("COIN","Coinbase"),
    ("HOOD","Robinhood"), ("SOFI","SoFi"),
    # 电商 / 零售
    ("COST","Costco"), ("SHOP","Shopify"), ("ETSY","Etsy"),
    ("CHWY","Chewy"), ("CPNG","Coupang"),
    # 出行 / 旅游
    ("UBER","Uber"), ("LYFT","Lyft"), ("DASH","DoorDash"),
    ("ABNB","Airbnb"), ("BKNG","Booking Holdings"),
    # 医疗
    ("VEEV","Veeva Systems"), ("ISRG","Intuitive Surgical"), ("DXCM","DexCom"),
    # 媒体
    ("DIS","Disney"), ("NYT","New York Times"),
    # 电动车
    ("RIVN","Rivian"), ("ENPH","Enphase Energy"),
    # 企业服务
    ("MSFT","Microsoft"), ("ORCL","Oracle"), ("INTU","Intuit"),
    ("WDAY","Workday"), ("ADSK","Autodesk"),
    # 消费品牌 / 餐饮
    ("SBUX","Starbucks"), ("MCD","McDonald's"), ("CMG","Chipotle"),
    ("LULU","lululemon"), ("NKE","Nike"), ("ONON","On Holding"),
    # 游戏
    ("EA","EA Sports"), ("TTWO","Take-Two"), ("U","Unity"),
    # 金融
    ("BLK","BlackRock"), ("GS","Goldman Sachs"), ("CME","CME Group"),
    # 中概 / 亚洲
    ("PDD","Pinduoduo"), ("BABA","Alibaba"), ("JD","JD.com"),
    ("BIDU","Baidu"), ("SE","Sea Limited"), ("MELI","MercadoLibre"),
    # 新兴
    ("PLTR","Palantir"), ("HIMS","Hims & Hers"), ("APP","AppLovin"),
    ("TTD","The Trade Desk"), ("CAVA","CAVA Group"), ("CELH","Celsius"),
]


def source_yahoo_trending():
    """从 Yahoo Finance 抓取趋势股票（补充用，AV 限频时的备用验证源）"""
    print("📡 [Source 4] Yahoo Finance Trending...", file=sys.stderr)
    try:
        url = "https://finance.yahoo.com/trending-tickers"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # 匹配 Yahoo Finance 趋势股票的 symbol
        matches = re.findall(r'data-symbol="([A-Z]{1,5})"', html)
        seen = set()
        candidates = []
        for sym in matches:
            if sym in seen or is_likely_etf_or_fund(sym):
                continue
            seen.add(sym)
            candidates.append({
                "symbol": sym,
                "name": "",
                "source": "yahoo_trending",
                "reason": "Yahoo Trending",
            })
            if len(candidates) >= 20:
                break
        print(f"  ✅ 获取 {len(candidates)} 个候选", file=sys.stderr)
        return candidates
    except Exception as e:
        print(f"  ⚠️ Yahoo Finance 失败: {e}", file=sys.stderr)
        return []


def validate_yahoo_quote(symbol):
    """
    用 Yahoo Finance Quote API 验证市值（无限频限制，AV 限频后的备用验证）
    返回 ("valid", name, mc) | ("invalid", None, None) | ("error", "", 0)
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
        instrument_type = meta.get("instrumentType", "").upper()
        if instrument_type not in ("EQUITY", ""):
            return "invalid", None, None
        market_cap = meta.get("marketCap", 0)
        if market_cap and market_cap < MIN_MARKET_CAP:
            return "invalid", None, None
        symbol_name = meta.get("shortName", "")
        if symbol_name:
            name_upper = symbol_name.upper()
            for kw in ["ETF", "TRUST", "FUND", "INDEX", "WARRANT", "PREFERRED"]:
                if kw in name_upper:
                    return "invalid", None, None
        return "valid", symbol_name, market_cap or 0
    except Exception:
        return "error", "", 0


def source_fallback_pool(done_symbols):
    """固定候选池：随机打散，排除已完成，作为最后兜底
    
    建议每季度更新一次候选池，保持与当前市场主题的相关性。
    更新原则：替换为当前季度市场关注度高、尚未被分析过的公司。
    """
    print("📡 [Source 5] 固定候选池兜底...", file=sys.stderr)
    pool = [{"symbol": s, "name": n, "source": "fallback_pool", "reason": "Curated"}
            for s, n in FALLBACK_POOL if s not in done_symbols]
    random.shuffle(pool)
    print(f"  ✅ 可用 {len(pool)} 家", file=sys.stderr)
    return pool


# ─────────────────────────────────────────────
# AV OVERVIEW 验证（辅助）
# ─────────────────────────────────────────────

def validate_av_overview(symbol):
    """
    返回 ("valid", name, mc) | ("invalid", None, None) | ("ratelimit", "", 0) | ("error", "", 0)
    """
    try:
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        if "Note" in data or "Information" in data:
            return "ratelimit", "", 0
        if not data or "Symbol" not in data:
            return "invalid", None, None

        if "common stock" not in data.get("AssetType", "").lower():
            return "invalid", None, None

        name = data.get("Name", "").upper()
        for kw in ["WARRANT", " UNIT", " RIGHT", "NOTE", "DEBENTURE", "PREFERRED"]:
            if kw in name:
                return "invalid", None, None

        try:
            mc = int(data.get("MarketCapitalization", "0") or "0")
        except ValueError:
            mc = 0

        if mc < MIN_MARKET_CAP:
            return "invalid", None, None

        return "valid", data.get("Name", ""), mc

    except Exception:
        return "error", "", 0


# ─────────────────────────────────────────────
# 主逻辑
# ─────────────────────────────────────────────

def main():
    # 1. 确定本地输出目录：优先读取环境变量，其次默认使用 ~/Documents/BusinessModelCraft
    output_dir = resolve_output_root()

    print(f"扫描本地: {output_dir}", file=sys.stderr)
    local_slugs, local_symbols = get_local_analyzed(str(output_dir))
    print(f"本地已分析 symbols: {sorted(local_symbols)}", file=sys.stderr)

    published_slugs = get_published_slugs()
    print(f"网站已发布 slugs: {sorted(published_slugs)}", file=sys.stderr)

    done_slugs = local_slugs | published_slugs
    done_symbols = local_symbols

    # 2. 多源采集（Google Finance 为主力，AV 补充，StockAnalysis 备用，Yahoo Trending 补充）
    source_stats = {}
    realtime_candidates = []

    # 数据源优先级：
    # 1. Google Finance（主力，无需 API Key）
    # 2. StockAnalysis（无需 API Key）
    # 3. Yahoo Trending（无需 API Key）
    # 4. Alpha Vantage（最低优先级，需用户自行配置 API Key）
    for name, fn, kwargs in [
        ("google_finance",  source_google_finance, {}),
        ("stockanalysis",   source_stockanalysis,  {}),
        ("yahoo_trending",  source_yahoo_trending, {}),
        ("alpha_vantage",   source_alpha_vantage,  {}),
    ]:
        try:
            results = fn(**kwargs)
            source_stats[name] = len(results)
            realtime_candidates.extend(results)
        except Exception as e:
            print(f"  ❌ {name} 异常: {e}", file=sys.stderr)
            source_stats[name] = 0

    # 3. 实时候选去重 + 过滤已完成
    seen = set()
    filtered_realtime = []
    for c in realtime_candidates:
        sym = c["symbol"].upper()
        if sym in seen or sym in done_symbols:
            continue
        # slug 去重（用 symbol 的 lower case 近似）
        if sym.lower() in done_slugs:
            continue
        seen.add(sym)
        filtered_realtime.append(c)

    print(f"\n实时候选去重后: {len(filtered_realtime)} 个", file=sys.stderr)

    # 4. 验证实时候选（AV OVERVIEW），带来源优先级
    source_priority = {"google_finance": 1, "stockanalysis": 2, "yahoo_trending": 3, "alpha_vantage": 9}
    filtered_realtime.sort(key=lambda c: source_priority.get(c.get("source", ""), 9))

    selected = []
    av_calls = 0
    av_rate_limited = False

    for c in filtered_realtime:
        if len(selected) >= TARGET_RESULTS:
            break

        sym = c["symbol"]
        # Google Finance 已带公司名，可以做 ETF 名称二次过滤
        if is_likely_etf_or_fund(sym, c.get("name", "")):
            continue

        # 市值验证：AV 还有配额时验证，限频后改用 Yahoo Finance Quote API 验证
        if not av_rate_limited and av_calls < AV_MAX_CALLS:
            time.sleep(0.4)
            status, name, mc = validate_av_overview(sym)
            av_calls += 1
            if status == "ratelimit":
                av_rate_limited = True
                print(f"  ⚠️ AV 限频，后续候选改用 Yahoo Finance 验证", file=sys.stderr)
                # 立即尝试 Yahoo Finance 验证
                yf_status, yf_name, yf_mc = validate_yahoo_quote(sym)
                if yf_status == "invalid":
                    print(f"  ⛔ {sym} Yahoo 验证不达标", file=sys.stderr)
                    continue
                if yf_name:
                    c["name"] = yf_name
                if yf_mc:
                    c["market_cap"] = yf_mc
                selected.append(c)
            elif status == "invalid":
                print(f"  ⛔ {sym} 市值/类型不达标", file=sys.stderr)
                continue
            else:
                if name:
                    c["name"] = name
                if mc:
                    c["market_cap"] = mc
                selected.append(c)
        elif av_rate_limited:
            # AV 限频后：用 Yahoo Finance 验证（无限频限制）
            yf_status, yf_name, yf_mc = validate_yahoo_quote(sym)
            if yf_status == "invalid":
                print(f"  ⛔ {sym} Yahoo 验证不达标（AV 限频后）", file=sys.stderr)
                continue
            if yf_name:
                c["name"] = yf_name
            if yf_mc:
                c["market_cap"] = yf_mc
            selected.append(c)
        else:
            # AV 配额耗尽但未限频：Google Finance 来源直接放行（可信度高）；其他来源也放行
            selected.append(c)

    # 5. 实时候选不够时，从兜底池补充
    if len(selected) < TARGET_RESULTS:
        print(f"\n实时候选仅 {len(selected)} 个，从固定候选池补充...", file=sys.stderr)
        fallback = source_fallback_pool(done_symbols)
        source_stats["fallback_pool"] = len(fallback)
        for c in fallback:
            if len(selected) >= TARGET_RESULTS:
                break
            if c["symbol"] not in {s["symbol"] for s in selected}:
                selected.append(c)
    else:
        source_stats["fallback_pool"] = 0

    print(f"\n最终选出: {[(c['symbol'], c.get('source','')) for c in selected]}", file=sys.stderr)

    print(json.dumps({
        "candidates": selected,
        "meta": {
            "sources": source_stats,
            "realtime_filtered": len(filtered_realtime),
            "selected": len(selected),
        }
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
