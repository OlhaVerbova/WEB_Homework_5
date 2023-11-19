import aiohttp
import asyncio
import aiofiles
import datetime
import sys
import json


#Make the format of how we will output the currency rate to the console
def format_currency(response, focus_currency, date):
    currency_list = []
    for currency_data in response:
        currency_code = currency_data['currency']
        
        if currency_code in focus_currency:
            currency_list.append({
                date: {
                    f"{currency_code}": {
                        "sale": currency_data["saleRateNB"],
                        "purchase": currency_data["purchaseRateNB"]
                    }
                }
            })
    
    return currency_list

#Let's write the result to json to check the format
async def write_to_json_file(data, filename):
    async with aiofiles.open(filename, 'w') as fd:
        await fd.write(json.dumps(data, indent = 2))

async def main(num: int):
    result = []
    focus_currency = ["EUR", "USD"] #If we need more currency, it is enough to add it to this list

    for i in range(num):
        current_date = datetime.date.today() - datetime.timedelta(days=i)
        formatted_date = current_date.strftime("%d.%m.%Y")
        dynamic_url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={formatted_date}'

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(dynamic_url) as response:
                    if response.status == 200:
                        result_i = await response.json()                    
                        formatted_data = format_currency(result_i["exchangeRate"], focus_currency, formatted_date)                    
                        print(formatted_data) 
                        result.append(formatted_data)
                    else:
                        print(f"Error status: {response.status} for {dynamic_url}")
            except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError) as error:
                print(f"Error accessing {dynamic_url}: {error}")
    
    await write_to_json_file(result, "currency.json")     
    return result


if __name__ == "__main__":    
    number_of_days = int(sys.argv[1])
    if number_of_days > 10:
        print("The program can output course data for no more than the last 10 days. Please enter a value not exceeding 10.")
    else:
        asyncio.run(main(number_of_days))

    
