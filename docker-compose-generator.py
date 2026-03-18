import sys
CLIENTS = 2
OUTPUT = 1
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
                         "enviroment": [
                             "PYTHONUNBUFFERED=1",
                             "LOGGING_LEVEL=DEBUG"],
                         "networks": [
                             "testing_net"]
                            }
                        },
                 "networks":{
                     "testing_net":{
                         "ipam":{
                             "dirver": "default",
                              "config":[{"subnet":"172.25.125.0/24"}]
                              }
                            }
                        }
                }
    for n in range(client_amount):
        client = f"client{n+1}"
        yaml_dicc["services"][client] = {"container_name": client, "image": "client:latest", "entrypoint": "/client", "enviroment": [f"CLI_ID={n+1}", "CLI_LOG_LEVEL=DEBUG"], "networks":["testing_net"], "depends_on":["server"]}
    return yaml_dicc

if __name__ == "__main__":
    main()