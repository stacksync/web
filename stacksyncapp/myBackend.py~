

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
User = get_user_model()
import json
import requests
import datetime
from django.utils.timezone import utc

class myBackend(ModelBackend):
 

    def authenticate(self, username=None, password=None):


	url = 'http://cloudspaces.urv.cat:5000/v2.0/tokens'
	payload = {'auth': {'passwordCredentials': {'username': username, 'password': password}, 'tenantName': username}}
	headers = {'content-type': 'application/json'}

	r = requests.post(url, data=json.dumps(payload), headers=headers)

	response = r.status_code
	
	if response == 200:
		r.json()
		json_data = json.loads(r.content)
		token_id = json_data['access']['token']['id']
		date = json_data['access']['token']['expires']
		expdate = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

		try:
                	user = User.objects.get(username=username)
			user.token_id = token_id
			user.expdate = expdate
			user.save()

                except User.DoesNotExist:
			user = User(username = username, password = password, token_id = token_id, expdate = expdate)
			user.save()
		return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
