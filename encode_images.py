# import base64

# with open("mammooty.jpg", "rb") as image_file:
#     encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
# print(encoded_image)


import pickle
import json

# Your serialized data
serialized_data = b"\x80\x04\x95\xb7\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x04date\x94\x8c\n2023-12-08\x94\x8c\bcache_id\x94\x8c 1ad22983bd339a5aaf1bfba8c1bf7427\x94\x8c\x04time\x94\x8c\b09:00 PM\x94\x8c\atickets\x94]\x94(\x8c\x02A1\x94\x8c\x02B1\x94\x8c\x02C1\x94\x8c\x02B2\x94\x8c\x02C2\x94\x8c\x02B3\x94\x8c\x02C3\x94e\x8c\x0ctheatre_name\x94\x8c\akavitha\x94\x8c\rscreen_number\x94\x8c\x011\x94u."

# Deserialize the data
deserialized_data = pickle.loads(serialized_data)

# Convert to JSON
json_data = json.dumps(deserialized_data, indent=2)

# Print or use the JSON data
print(json_data)