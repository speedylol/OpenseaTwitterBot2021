import requests
import json 
import tweepy
import time
from datetime import datetime

class TweetAUTH():
    def __init__(self):
        # Enter twitter api keys here
        self.API_KEY = ''
        self.API_KEY_SECRET = ''

        self.ACCESS_TOKEN = ''
        self.ACCESS_TOKEN_SECRET = ''

    def authenticate(self):
        auth = tweepy.OAuthHandler(self.API_KEY, self.API_KEY_SECRET)
        auth.set_access_token(self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)

        api = tweepy.API(auth)
        # Verify credentials
        try:
            api.verify_credentials()
            return api
        except:
            return False

    def tweetSale(self, api, sale_data):
        asset_name = sale_data[0]
        asset_link = sale_data[1]
        sale_price = sale_data[2]
        payment_token = sale_data[3]
        usd_price = sale_data[4]
        token_id = sale_data[5]

        # Edit this according to the NFT names
        tweet_text = f'Blockchain Biker #{token_id} just sold for {sale_price} {payment_token} (${usd_price:.2f} USD)!\n @bikersnft #Bikersnft #rideordie #NFT \n{asset_link}'

        api.update_status(status=tweet_text)

class openseaSalesBot():

    def __init__(self):
        self.asset_range = 4
    
    def requestLastSales(self):
        # Request event data
        json_data = self.successfulEventData()
        return self.parseSuccesfulEventData(json_data)

    def successfulEventData(self):
        url = "https://api.opensea.io/api/v1/events"
        asset_contract_address = '0x15533781a650f0c34f587cdb60965cdfd16ff624' # NFT contract address
        
        querystring = {"only_opensea":"true","offset":"0","limit": str(self.asset_range), "asset_contract_address": asset_contract_address, "event_type": "successful"}
        response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)

        return json.loads(response.text)


    
    def parseSuccesfulEventData(self, json_dump):
        json_list = []
        # Loop through the last sales
        for i in range(self.asset_range):
            # json only contains the last sale info
            asset_info = json_dump['asset_events'][i]['asset']
            
            image_url = asset_info['image_url']
            punk_name = asset_info['name']
            token_id = asset_info['token_id']
            product_link = asset_info['permalink']
            
            # Seller info
            seller_info = json_dump['asset_events'][i]['seller']
            if(seller_info['user'] == None):
                seller_username = 'None'
            else:
                seller_username = seller_info['user']['username']
            seller_address = seller_info['address'] 
            
            # Buyer info
            buyer_info = json_dump['asset_events'][i]['winner_account']
            if(buyer_info['user'] == None):
                buyer_username = 'None'
            else:
                buyer_username = buyer_info['user']['username']
            buyer_address = buyer_info['address']
            
            payment_info = json_dump['asset_events'][i]['payment_token']
            payment_token = payment_info['symbol']
            
            sale_id = json_dump['asset_events'][i]['id']
            sale_price = int(json_dump['asset_events'][i]['total_price']) / 1000000000000000000
            usd_price = float(payment_info['usd_price'] ) * float(sale_price)
            
            json_info = {
                'asset_info': {
                    'asset_name': punk_name,
                    'asset_image': image_url,
                    'asset_link': product_link,
                },
                'seller_info': {
                    'seller_username': seller_username,
                    'seller_address': seller_address
                },
                'buyer_info': {
                    'buyer_username': buyer_username,
                    'buyer_address': buyer_address
                },
                'payment_token': payment_token,
                'usd_price': usd_price,
                'token_id': token_id,
                'sale_price': sale_price,
                'sale_id': sale_id
                
            }
            json_list.append(json_info)
        return json_list

    def runInstance(self):
        
        tweetBot = TweetAUTH()
        api = tweetBot.authenticate()

        if api == False:
            print('Error cant connect to twitter api')
            input()
        
        old_sale_list = self.requestLastSales()
        old_sale_id = [] 
        
        for i in range(self.asset_range):
            old_sale_id.append(old_sale_list[i]['sale_id'])

        while(True):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            new_sales = []

            try:
                new_sales_list = self.requestLastSales()
                new_sale_id = []

                for i in range(self.asset_range):
                    new_sale_id.append(new_sales_list[i]['sale_id'])

            except Exception as e:
                new_sales_list = old_sale_list
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print(f'[{current_time}] Error - {e}')
            
            new_sales = list(set(new_sale_id) - set(old_sale_id))
            
            if new_sales != []:

                for i in range(len(new_sales)):
                    print(f"[{current_time}] New  sale! - {new_sales[i]}")

                    for j in range(len(new_sales_list)):
                        if  new_sales_list[j]['sale_id'] == new_sales[i]:

                            # Data for tweet
                            asset_name = new_sales_list[j]['asset_info']['asset_name']
                            asset_link = new_sales_list[j]['asset_info']['asset_link']
                            sale_price = new_sales_list[j]['sale_price']
                            payment_token = new_sales_list[j]['payment_token']
                            usd_price = new_sales_list[j]['usd_price']
                            token_id = new_sales_list[j]['token_id']
                            
                            sale_data = [asset_name, asset_link, sale_price, payment_token, usd_price, token_id]
                            print(f"{sale_data[0]}")
                            print(f"BlockchainBiker #{token_id} Sold for {sale_data[2]}")



                            try:
                                tweetBot.tweetSale(api, sale_data)
                            except Exception as e:
                                print(f'Error: {e}')
                            break
                        
            else:
                print(f'[{current_time}] No new sales!')
            
            old_sale_id = new_sale_id
            old_sale_list = new_sales_list

            time.sleep(10) # Delay for requesting the opensea api

bot = openseaSalesBot()
bot.runInstance()
