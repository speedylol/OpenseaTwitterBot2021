import requests
import json

discord_webhook_url = 'https://discordapp.com/api/webhooks/INSERTWEBHOOKURLHERE'



class listingBot():

	def __init__(self):
		self.asset_range = 10

	def requestLastListing(self):
		json_data = self.successfulEventData()
		return self.parseSuccessfulEventData(json_data)

	def successfulEventData(self):
		url = "https://api.opensea.io/api/v1/events"
		asset_contract_address = "0x15533781a650f0c34f587cdb60965cdfd16ff624"

		querystring = {"only_opensea":"true","offset":"0","limit": str(self.asset_range), "asset_contract_address": asset_contract_address, "event_type": "created"}
		response = requests.request("GET", url, headers={"Accept": "application/json"}, params=querystring)
		return json.loads(response.text)


	def parseSuccessfulEventData(self, json_dump):
		json_list = []

		for i in range(self.asset_range):

			asset_info = json_dump['asset_events'][i]['asset']
			image_url = asset_info['image_url']
			biker_name = asset_info['name']
			token_id = asset_info['token_id']
			product_link = asset_info['permalink']


			seller_info = json_dump['asset_events'][i]['seller']

			if(seller_info['user'] == None):
				seller_username = 'None'
			else:
				seller_username = seller_info['user']['username']
			seller_address = seller_info['address']


			payment_info = json_dump['asset_events'][i]['payment_token']
			payment_token = payment_info['symbol']

			sale_id = json_dump['asset_events'][i]['id']
			sale_price = int(json_dump['asset_events'][i]['ending_price']) / 1000000000000000000
			usd_price = float(payment_info['usd_price'] ) * float(sale_price)

			json_info = {
			    'asset_info': {
			        'asset_name': biker_name,
			        'asset_image': image_url,
			        'asset_link': product_link,
			    },
			    'seller_info': {
			        'seller_username': seller_username,
			        'seller_address': seller_address
			    },

			    'payment_token': payment_token,
			    'usd_price': usd_price,
			    'token_id': token_id,
			    'sale_price': sale_price,
			    'sale_id': sale_id
			    
			}
			json_list.append(json_info)
		return json_list


	def sendWebhook(self, listing_json):

		asset_info = listing_json['asset_info']
		seller_info = listing_json['seller_info']
		payment_token = listing_json['payment_token']
		sale_price = listing_json['sale_price']

		json_info = json.dumps(
		{
		    'embeds': [
		        {
		            'title': "BlockchainBiker was Listed!",
		            'url': 'https://opensea.io/assets/0x9c0ffc9088abeb2ea220d642218874639229fa7a/2339',
		            'fields': [ 
		                {
		                    'name': '**Sale price**',
		                    'value': '1 ETH ($4000 USD)',
		                    'inline': 'false'
		                },
		                {
		                    'name': '**Buyer**',
		                    'value': "Speedylol",
		                    'inline': 'true'
		                },
		                {
		                    'name': '**Seller**',
		                    'value': "PaperHandBaby",
		                    'inline': 'true'
		                }
		            ],
		            'image': {
		                'url': "https://lh3.googleusercontent.com/erovF3fefq0WqtdQB7GM5f0K9yIvAO-_wBPBLL8a8r8nPeLDHAoAvrlwr0qEQgSvg5gNX9odojD-sM08PtrH3a2zmuxA0Jca1E0QTJY"

		            },
		            'footer': {
		                'text': f'@infophilic', # Change this to your projects name
		                'icon_url': 'https://pipedream.com/s.v0/app_13GhY1/logo/orig' # Change this to your projects logo
		            }
		        }
		    ]
		}
		)

		requests.post(discord_webhook_url, data=json_info, headers={"Content-Type": "application/json"})    	


	def runInstance(self):

		old_sale_list = self.requestLastListing()
		old_sale_id = [] 

		for i in range(self.asset_range):
			old_sale_id.append(old_sale_list[i]['sale_id'])

		while(True):
			now = datetime.now()
			current_time = now.strftime("%H:%M:%S")
			new_sales = []

			try:
				new_sales_list = self.requestLastListing()
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

							asset_name = new_sales_list[j]['asset_info']['asset_name']
							asset_link = new_sales_list[j]['asset_info']['asset_link']
							sale_price = new_sales_list[j]['sale_price']
							payment_token = new_sales_list[j]['payment_token']
							usd_price = new_sales_list[j]['usd_price']
							token_id = new_sales_list[j]['token_id']
			                
							sale_data = [asset_name, asset_link, sale_price, payment_token, usd_price, token_id]
							print(f"{sale_data[0]}")
							print(f"BlockchainBiker #{token_id} posted for {sale_data[2]}")

		            
							try:
								self.sendWebhook(new_sales_list[j])
							except Exception as e:
								print(f'Error: {e}') 

			else:
				print(f'[{current_time}] No new listings!')


			old_sale_id = new_sale_id
			old_sale_list = new_sales_list
			time.sleep(3)

bot = listingBot()
bot.runInstance()


