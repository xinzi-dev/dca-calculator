import requests
import numpy as np
import pandas as pd
from datetime import datetime
from base_dca_calculator import BaseDCACalculator, PriceType  # 你可以根据项目结构调整导入路径


class CryptoDCACalculator(BaseDCACalculator):
    def __init__(self, symbol: str, **kwargs):
        self.symbol = symbol.lower()
        super().__init__(**kwargs)

    def get_price_data(self, price_type: PriceType) -> pd.Series:
        # 映射常见币种的 CoinGecko ID
        symbol_map = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "sol": "solana",
            "bnb": "binancecoin",
            "ada": "cardano",
        }

        coin_id = symbol_map.get(self.symbol)
        if not coin_id:
            raise ValueError(f"不支持的币种 symbol: {self.symbol}")

        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "max",
            "interval": "daily"
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ValueError("无法获取 CoinGecko 数据")

        data = response.json()
        if "prices" not in data:
            raise ValueError("API 响应中缺少价格数据")

        df = pd.DataFrame(data["prices"], columns=["timestamp", "close"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
        df.set_index("date", inplace=True)

        # 模拟生成 OHLC 数据（实际 API 没有返回完整 OHLC）
        df["open"] = df["close"] * (1 + np.random.uniform(-0.01, 0.01, len(df)))
        df["high"] = df[["open", "close"]].max(axis=1) * 1.01
        df["low"] = df[["open", "close"]].min(axis=1) * 0.99
        df["median"] = (df["high"] + df["low"]) / 2

        # 只保留用户指定时间范围和价格类型
        mask = (df.index >= self.start_date.date()) & (df.index <= self.end_date.date())
        df_filtered = df.loc[mask]

        if price_type.value not in df_filtered.columns:
            raise ValueError(f"无效的价格类型: {price_type}")

        return df_filtered[price_type.value]