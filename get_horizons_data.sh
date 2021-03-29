#!/bin/bash

#By Lucas Kolanz

#move these lines to install file eventually (when one exists)
chmod +x horizons.sh
chmod +x horizons_expect
chmod +x ftp_transpher.sh
chmod +x get_horizons_data_expect

#runs an expect script to get data from NASA Horizons 
./horizons_expect $1 $2 $3 $4 $5 $6 $7 $8

rand=$2

#If you only want the initial positon and velocity of a body
if [[ $1 == "state_vector" ]]; then
	input="./data_dump/ftp/ftp_info_state_vector_${rand}.log"
	file_name="value must change"

	#reads in Horizons file, fetched from 'horizons_expect' which 
	#	contains the ftp data from Horizons
	while IFS= read -r line
	do
		test_me="${line%:*}"
		value="${line#*:}"
		#remove leading whitespace
		test_me="${test_me#"${test_me%%[![:space:]]*}"}"
		value="${value#"${value%%[![:space:]]*}"}"
		#remove trailing whitespace
		test_me="${test_me%"${test_me##*[![:space:]]}"}"
		value="${value%"${value##*[![:space:]]}"}"

	  if [[ "${test_me}" == "File name" ]]; then
	  	file_name="${value}"
	  elif [[ "${test_me}" == "Machine name" ]]; then
	  	machine_name="${value}"
	  elif [[ "${test_me}" == "Directory" ]]; then
	  	dir="${value#*\"}"
	  	dir="${dir%*\"*}"
	  fi
	done < "$input"

	#gets the initial positon and velocity data from the file we got
	#	from ftp horizons
	./get_horizons_data_expect "${file_name}" "${machine_name}" "${dir}" 

	mv ./data_dump/ftp/${file_name} ./data_dump/ftp/state_vector_${2}.log
	# rm $input

#If you only want the mass and radius of a body
elif [[ $1 == "other" ]]; then
	input="./data_dump/ftp/ftp_info_other_${rand}.log"
	file_name="value must change"
	while IFS= read -r line
	do
		test_me="${line%:*}"
		value="${line#*:}"
		#remove leading whitespace
		test_me="${test_me#"${test_me%%[![:space:]]*}"}"
		value="${value#"${value%%[![:space:]]*}"}"
		#remove trailing whitespace
		test_me="${test_me%"${test_me##*[![:space:]]}"}"
		value="${value%"${value##*[![:space:]]}"}"

	  if [[ "${test_me}" == "File name" ]]; then
	  	file_name="${value}"
	  elif [[ "${test_me}" == "Machine name" ]]; then
	  	machine_name="${value}"
	  elif [[ "${test_me}" == "Directory" ]]; then
	  	dir="${value#*\"}"
	  	dir="${dir%*\"*}"
	  fi
	done < "$input"

	./get_horizons_data_expect "${file_name}" "${machine_name}" "${dir}" 

	mv ./data_dump/ftp/${file_name} ./data_dump/ftp/other_${2}.log
	# rm $input


#If you only want both the initial position and velocity and 
#	the mass and radius of a body
elif [[ $1 == "both" ]]; then
	input="./data_dump/ftp/ftp_info_other_${rand}.log"
	file_name="value must change"
	while IFS= read -r line
	do
		test_me="${line%:*}"
		value="${line#*:}"
		#remove leading whitespace
		test_me="${test_me#"${test_me%%[![:space:]]*}"}"
		value="${value#"${value%%[![:space:]]*}"}"
		#remove trailing whitespace
		test_me="${test_me%"${test_me##*[![:space:]]}"}"
		value="${value%"${value##*[![:space:]]}"}"

		# echo "${line}"
		# echo "${test_me}"
		# echo "${value}"

	  if [[ "${test_me}" == "File name" ]]; then
	  	file_name="${value}"
	  elif [[ "${test_me}" == "Machine name" ]]; then
	  	machine_name="${value}"
	  elif [[ "${test_me}" == "Directory" ]]; then
	  	dir="${value#*\"}"
	  	dir="${dir%*\"*}"
	  fi
	done < "$input"

	./get_horizons_data_expect "${file_name}" "${machine_name}" "${dir}" 

	mv ./data_dump/ftp/${file_name} ./data_dump/ftp/other_${2}.log
	# rm $input

	input="./data_dump/ftp/ftp_info_state_vector_${rand}.log"
	file_name="value must change"
	while IFS= read -r line
	do
		test_me="${line%:*}"
		value="${line#*:}"
		#remove leading whitespace
		test_me="${test_me#"${test_me%%[![:space:]]*}"}"
		value="${value#"${value%%[![:space:]]*}"}"
		#remove trailing whitespace
		test_me="${test_me%"${test_me##*[![:space:]]}"}"
		value="${value%"${value##*[![:space:]]}"}"

		# echo "${line}"
		# echo "${test_me}"
		# echo "${value}"

	  if [[ "${test_me}" == "File name" ]]; then
	  	file_name="${value}"
	  elif [[ "${test_me}" == "Machine name" ]]; then
	  	machine_name="${value}"
	  elif [[ "${test_me}" == "Directory" ]]; then
	  	dir="${value#*\"}"
	  	dir="${dir%*\"*}"
	  fi
	done < "$input"

	./get_horizons_data_expect "${file_name}" "${machine_name}" "${dir}" 

	mv ./data_dump/ftp/${file_name} ./data_dump/ftp/state_vector_${2}.log
	# rm $input

fi
# echo "FINISHED GET_HORIZONS_DATA.SH"

