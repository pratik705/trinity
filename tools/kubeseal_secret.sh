#!/bin/bash
input_path=$1
public_cert=$2

display_usage() { 
    echo -e "\nUsage:\n\t$0 DIRECTORY_PATH  KUBESEAL_PUBLIC_CERT \n"
    } 
    if [  $# != 2 ] 
    then 
        display_usage
	exit 1
    fi 
 
if [ ! -d $input_path ] 
then 
    echo "ERROR: Input path '$input_path' does not exist"
    exit 1 
fi

if [ ! -f $public_cert ]
then
    echo "ERROR: Certificate file '$public_cert' does not exist"
    exit 1
fi

echo "Identifying the files of kind 'secret'..."
secret_files=`grep --include=\*.yaml -rlnw $input_path -e '^kind: Secret'`
if [ -z "$secret_files" ]; then
    echo "INFO: No Secret files to encrypt using Kubeseal"
    exit 0
fi

echo "Secret files" $secret_files
touch $input_path/.gitignore
for file in $secret_files ; do echo $file;  kubeseal --scope cluster-wide --allow-empty-data \
    --cert=$2 -o yaml < $file > `dirname $file`/encrypted-`basename $file` ; if [ $? -eq 1 ] ; \
    then echo "ERROR: Encryption failed" ; exit 1 ; fi ; grep -qxF `basename $file` $input_path/.gitignore \
    || echo `basename $file` >> $input_path/.gitignore  ; done
echo "INFO: Encryption successful" 
