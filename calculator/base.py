# 定义抽象类和接口

from abc import ABC, abstractmethod
from enum import Enum
import pandas as pd
from datetime import timedelta


class PriceType(Enum):
    OPEN = "open"
    CLOSE = "close"
    HIGH = "high"
    LOW = "low"
    MEDIAN = "median"


class BaseDCACalculator(ABC):
    def __init__(
        self,
        start_date,
        end_date,
        frequency='monthly',
        amount_per_period=100,
        price_type=PriceType.CLOSE
    ):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.frequency = frequency
        self.amount = amount_per_period
        self.price_type = price_type
        self.trade_log = []

        # 调用子类实现的价格获取方法，传入 price_type 参数
        self.price_data = self.get_price_data(price_type=self.price_type)

    @abstractmethod
    def get_price_data(self, price_type: PriceType) -> pd.Series:
        """
        子类必须实现：返回指定价格类型的数据（以日期为索引的 Series）
        """
        pass

    def _get_investment_dates(self):
        """
        生成定投日期序列，自动跳过没有数据的日期
        """
        dates = []
        current = self.start_date
        while current <= self.end_date:
            if current in self.price_data.index:
                dates.append(current)
            else:
                # 顺延到下一个有数据的日期
                next_day = current
                while next_day not in self.price_data.index and next_day <= self.end_date:
                    next_day += timedelta(days=1)
                if next_day in self.price_data.index:
                    dates.append(next_day)

            # 时间步进
            offset = {
                'daily': pd.DateOffset(days=1),
                'weekly': pd.DateOffset(weeks=1),
                'monthly': pd.DateOffset(months=1)
            }.get(self.frequency, pd.DateOffset(months=1))
            current += offset
        return dates

    def run_investment(self):
        """
        执行定投操作：按日期买入固定金额的资产
        """
        for date in self._get_investment_dates():
            price = self.price_data[date]
            shares = self.amount / price
            self.trade_log.append({
                'date': date,
                'price': price,
                'shares': shares,
                'amount': self.amount
            })

    def calculate_summary(self):
        """
        汇总定投结果：总投入、市值、收益、收益率
        """
        df = pd.DataFrame(self.trade_log)
        if df.empty:
            return {
                'total_invested': 0,
                'total_shares': 0,
                'latest_price': 0,
                'current_value': 0,
                'profit': 0,
                'return_rate': 0
            }

        total_invested = df['amount'].sum()
        total_shares = df['shares'].sum()
        latest_price = self.price_data.iloc[-1]
        current_value = total_shares * latest_price
        profit = current_value - total_invested
        return_rate = profit / total_invested

        return {
            'total_invested': total_invested,
            'total_shares': total_shares,
            'latest_price': latest_price,
            'current_value': current_value,
            'profit': profit,
            'return_rate': return_rate
        }

    def display_summary(self):
        """
        打印投资收益摘要
        """
        summary = self.calculate_summary()
        print("\n 定投收益摘要")
        for k, v in summary.items():
            label = k.replace('_', ' ').title()
            if "rate" in k:
                print(f"{label}: {v:.2%}")
            else:
                print(f"{label}: ${v:.2f}")