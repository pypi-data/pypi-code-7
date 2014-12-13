channels = [
	{
		"name": "twitter",
		"pattern": { 
			"user_name": "{{UserName}}", 
			"published": "{{CreatedAt}}", 
			"short_url": "{{LinkToTweet}}",
			"text": "{{Text}}"
		}
	},
	{
		"name": "yo",
		"pattern": {
			"published": "{{ReceivedAt}}",
			"from": "{{From}}" 
		}
	},
	{
		"name": "craigslist",
		"pattern": {
			"text": "{{PostContent}}",
			"title": "{{PostTitle}}",
			"url": "{{PostUrl}}",
			"published": "{{PostPublished}}"
		}
	},
	{
		"name":"instagram",
		"pattern": {
			"caption": "{{Caption}}",
			"url": "{{Url}}",
			"source_url": "{{SourceUrl}}",
			"username": "{{Username}}",
			"published": "{{CreatedAt}}"
		}
	}
]
