from random import choice

class VPC:
    def __init__(self, client):
        self._client = client
        """ :type : pyboto3.ec2 """

    def create_vpc(self, cidr):
        print('Creating a VPC...')
        return self._client.create_vpc(
            CidrBlock=f'{cidr}'
        )

    def add_name_tag(self, resource_id, resource_name):
        create_tag_response_list = []
        for count, resource in enumerate(resource_id):
            print(f'Adding {resource_name}-{count} name tag {count+1}/{len(resource_id)} to the {resource}')
            create_tag_response = self._client.create_tags(
                Resources=[resource],
                Tags=[{
                    'Key': 'Name',
                    'Value': f"{resource_name}-{count}"
                }]
            )
            create_tag_response_list.append(create_tag_response)
        return create_tag_response_list

    def create_internet_gateway(self):
        print('Creating an Internet Gateway...')
        return self._client.create_internet_gateway()

    def attach_igw_to_vpc(self, vpc_id, igw_id):
        print('Attaching Internet Gateway ' + igw_id + ' to VPC ' + vpc_id)
        return self._client.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )

    def describe_availability_zones(self, region):
        response = self._client.describe_availability_zones(
        Filters=[
            {
                'Name': 'region-name',
                'Values': [
                    f'{region}',
                ]
            },
        ]
        )
        zones = []
        response = response['AvailabilityZones']
        for vpc in response:
            zones.append(vpc['ZoneName'])
        return zones

    def create_subnet(self, vpc_id, zones, number_of_subnets):
        subnet_ids = []
        for count, subnet in enumerate(range(number_of_subnets)):
            cidr = f'10.0.{count}.0/24'
            print(f'Creating a subnet {count+1}/{number_of_subnets} for VPC {vpc_id} with CIDR block {cidr}')
            availability_zone = choice(zones)
            create_subnet_response = self._client.create_subnet(
                VpcId=vpc_id,
                CidrBlock=cidr,
                AvailabilityZone=f'{availability_zone}',
            )
            subnet_ids.append(create_subnet_response['Subnet']['SubnetId'])
        return subnet_ids

    def create_public_route_table(self, vpc_id, number_of_public_subnets):
        public_route_table_id_list = []
        for count, public_rt in enumerate(range(0,number_of_public_subnets)):
            print(f'Creating public route table {count+1}/{number_of_public_subnets} for VPC: {vpc_id}')
            public_route_table_response = self._client.create_route_table(VpcId=vpc_id)
            public_route_table_id_list.append(public_route_table_response['RouteTable']['RouteTableId'])
        return public_route_table_id_list

    def create_igw_route_to_public_route_table(self, rtb_id_list, igw_id):
        responses = []
        for count, rtb_id in enumerate(rtb_id_list):
            print(f'Adding internet route {count+1}/{len(rtb_id_list)} for IGW {igw_id} to public route table {rtb_id}')
            route_response = self._client.create_route(
                RouteTableId=rtb_id,
                GatewayId=igw_id,
                DestinationCidrBlock='0.0.0.0/0'
            )
            responses.append(route_response)
        return responses

    def associate_subnet_with_route_table(self, subnet_id_list, rtb_id_list):
        for count, association in enumerate(range(0,len(subnet_id_list))): 
            print(f'Associating public subnet {count+1}/{len(subnet_id_list)} ({subnet_id_list[count]}) with public route table {rtb_id_list[count]}')
            self._client.associate_route_table(
                SubnetId=subnet_id_list[count],
                RouteTableId=rtb_id_list[count]
            )
