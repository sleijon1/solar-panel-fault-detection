clean-txt:
	@echo "Removing generated text-files.."
	rm air_humidity_id.txt
	rm air_pressure_id.txt
	rm air_temperature_id.txt
	rm precipitation_id.txt
	rm cloud_coverage_id.txt
	rm data.txt
clean-csv:
	@echo "Removing generated csv-files.."
	rm smhi.csv
