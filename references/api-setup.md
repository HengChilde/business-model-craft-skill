# Alpha Vantage API Key 配置说明

脚本在自动选股时支持通过 Alpha Vantage API 验证候选公司的市值和基本信息。此功能为**最低优先级**，仅在 Google Finance 和 StockAnalysis 数据源都无法提供足够候选时才会用到。

**如何获取 API Key：**
1. 访问 [https://www.alphavantage.co](https://www.alphavantage.co)
2. 点击页面上的 **"Get your free API key today"**
3. 填写邮箱地址即可免费申请（无需信用卡）
4. 免费版每分钟限 5 次请求、每天 25 次，足以支持偶发使用

**配置方式（二选一）：**

方法 A（推荐，不修改代码）：
```bash
export ALPHA_VANTAGE_API_KEY="your_api_key_here"
python3 scripts/fetch_stock_data.py
```

方法 B（直接修改脚本）：
打开 `scripts/fetch_stock_data.py`，修改 `ALPHA_VANTAGE_API_KEY` 变量：
```python
ALPHA_VANTAGE_API_KEY = "your_api_key_here"
```

**不配置也没关系**：脚本会优先使用 Google Finance 和 StockAnalysis，它们无需 API Key 即可工作。Alpha Vantage 仅作辅助验证。
