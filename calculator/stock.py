import yfinance as yf
import pandas as pd
from datetime import timedelta
from base_dca_calculator import BaseDCACalculator, PriceType


class StockDCACalculator(BaseDCACalculator):
    def __init__(self, ticker: str, **kwargs):
        """
        初始化：指定股票代码 ticker（如 AAPL、MSFT 等）
        """
        self.ticker = ticker.upper()
        super().__init__(**kwargs)

    def get_price_data(self, price_type: PriceType) -> pd.Series:
        """
        获取股票价格数据，返回 pd.Series（日期索引）
        支持 PriceType 中定义的价格类型
        """
        df = yf.download(
            self.ticker,
            start=self.start_date,
            end=self.end_date + timedelta(days=1),  # 包括结束日期
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            raise ValueError(f" 无法获取股票数据: {self.ticker}")

        # 计算中位数价格
        df["Median"] = (df["High"] + df["Low"]) / 2

        # 映射价格类型
        column_map = {
            PriceType.OPEN: "Open",
            PriceType.CLOSE: "Close",
            PriceType.HIGH: "High",
            PriceType.LOW: "Low",
            PriceType.MEDIAN: "Median"
        }

        column = column_map.get(price_type)
        if column not in df.columns:
            raise ValueError(f" 不支持的价格类型: {price_type}")

        price_series = df[column]
        price_series.index = price_series.index.date  # 使用纯日期作为索引
        return price_series