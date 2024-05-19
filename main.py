import aiohttp
import asyncio
import datetime
from typing import Dict, List

class ExchangeRateFetcher:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date={}"

    def __init__(self, days: int):
        if days > 10:
            raise ValueError("The maximum allowed number of days is 10.")
        self.days = days

    async def fetch_exchange_rate(self, session: aiohttp.ClientSession, date: str) -> Dict[str, Dict[str, Dict[str, float]]]:
        url = self.BASE_URL.format(date)
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error fetching data: {response.status}")
                data = await response.json()
                rates = data['exchangeRate']
                result = {
                    date: {
                        'EUR': self._extract_rate(rates, 'EUR'),
                        'USD': self._extract_rate(rates, 'USD')
                    }
                }
                return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return {}

    def _extract_rate(self, rates: List[Dict], currency: str) -> Dict[str, float]:
        for rate in rates:
            if rate.get('currency') == currency:
                return {
                    'sale': rate['saleRate'],
                    'purchase': rate['purchaseRate']
                }
        return {}

    async def get_exchange_rates(self) -> List[Dict[str, Dict[str, Dict[str, float]]]]:
        today = datetime.datetime.now()
        dates = [(today - datetime.timedelta(days=i)).strftime('%d.%m.%Y') for i in range(self.days)]
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_exchange_rate(session, date) for date in dates]
            results = await asyncio.gather(*tasks)
            return [result for result in results if result]

def print_exchange_rates(rates: List[Dict[str, Dict[str, Dict[str, float]]]]):
    for rate in rates:
        for date, currencies in rate.items():
            print(f"{date}:")
            for currency, values in currencies.items():
                print(f"  {currency}: sale - {values['sale']}, purchase - {values['purchase']}")

if __name__ == "__main__":
    days = input("Введіть бажану кількість днів (не більше 10): ")
    try:
        days = int(days)
        if days > 10 or days <= 0:
            raise ValueError("Кількість днів має бути від 1 до 10.")
    except ValueError:
        print("Некоректне значення. Будь ласка, введіть ціле число від 1 до 10.")
        exit()

    fetcher = ExchangeRateFetcher(days=days)
    exchange_rates = asyncio.run(fetcher.get_exchange_rates())
    print_exchange_rates(exchange_rates)
