import sys
CLIENTS = 2
OUTPUT = 1
import random
from datetime import datetime
def main():
    if len(sys.argv) > 2:
        generated_yaml = yaml_generator(int(sys.argv[CLIENTS]))
        with open(sys.argv[OUTPUT], 'w') as f:
            write_yaml(f, generated_yaml, 0)
        f.close()
        return 0
    else:
        print("Incorrect amount of parameter please input: docker-copose-generate.py ${output file name} ${amount of clients}")
        return 1

def write_yaml(output_file, data, level, listing=False):
    indent = "   " * level
    if listing:
        indent += "- "
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) or isinstance(value, list):
                output_file.write(f"{indent}{key}:\n")
                write_yaml(output_file, value, level+1)
            else:
                output_file.write(f"{indent}{key}: {value}\n")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) or isinstance(item, list):
                write_yaml(output_file, item, level+1, True)
            else:
                output_file.write(f"{indent}- {item}\n")
    return

def yaml_generator(client_amount):
    yaml_dicc = {"name": "tp0",
                 "services":{
                     "server":{
                         "container_name": "server",
                         "image": "server:latest",
                         "entrypoint": "python3 /main.py",
                         "environment": [
                             "PYTHONUNBUFFERED=1",
                            ],
                         "networks": [
                             "testing_net"],
                         "volumes": [
                             "./server/config.ini:/config.ini"]
                            }
                        },
                 "networks":{
                     "testing_net":{
                         "ipam":{
                             "driver": "default",
                              "config":[{"subnet":"172.25.125.0/24"}]
                              }
                            }
                        }
                }
    for n in range(client_amount):
        client = f"client{n+1}"
        client_name = f"client{n+1}"
        client_last_name = f"client{n+1}erez"
        dni = n+1 + 10 ** 7
        birthdate = str(datetime.strptime(f"2000-03-{n+1}", "%Y-%m-%d").date())
        lottery_number=random.randint(1, 9999)
        yaml_dicc["services"][client] = {"container_name": client, "image": "client:latest", "entrypoint": "/client", 
                                         "environment": [f"CLI_ID={n+1}", f"CLI_NAME={client_name}", f"CLI_LASTNAME={client_last_name}", f"CLI_DNI={dni}",f"CLI_BIRTHDATE={birthdate}", f"CLI_NUMBER={lottery_number}"], "networks":["testing_net"],
                                        "depends_on":["server"], "volumes": ["./client/config.yaml:/config.yaml", f"./.data/agency-{n+1}.csv:/agency-{n+1}.csv"]}
    return yaml_dicc

if __name__ == "__main__":
    main()