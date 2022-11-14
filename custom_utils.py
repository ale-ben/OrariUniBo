def sanitize_path(in_path):
	path = in_path.replace(" ", "_")
	path = path.replace("/", "-")
	path = path.replace("\\", "-")
	path = path.replace(":", "-")
	path = path.replace("\n", "-")
	path = path.replace("-_-", "-")
	path = path.replace("_-_", "-")

	return path