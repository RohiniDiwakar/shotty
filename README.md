##shotty
Atomating EC2 backup with snapshots

##About
This is a demo project and uses boto3 to manage AWS EC2 instances

##configuration
Shotty uses the configuration file created by aws cli e.g

`aws configure --profile shotty`

##Running
`pipenv run python shotty/shotty.py <command> <--project=PROJECT>`

*command* 
    #instances : *subcommands* are list, start, stop, snapshot
    #volumes: *subcommands* are list
    #snapshots:  *subcommands* are list
*project* is optional


