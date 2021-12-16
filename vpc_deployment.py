from vpc import VPC
from ec2 import EC2
import boto3
import json


def main():

    configuration_file = open(r'config.json')
    configuration_data = json.load(configuration_file)
    number_of_vpcs = configuration_data['NumberOfVPCs']
    number_of_private_subnets = configuration_data['NumberOfPrivateSubnets'] 
    number_of_public_subnets = configuration_data['NumberOfPublicSubnets']
    number_of_subnets = number_of_public_subnets + number_of_private_subnets
    region = configuration_data['Region']
    cidr_block = configuration_data['CIDR_Block']

    # Create a VPC
    ec2_client = boto3.client('ec2', region_name=region)
    vpc = VPC(ec2_client)

    vpc_response = vpc.create_vpc(cidr_block)

    

    # Add name tag to VPC
    vpc_name = 'Boto3-VPC'
    vpc_id = vpc_response['Vpc']['VpcId']
    print('VPC created: ' + str(vpc_id))
    vpc_id_list = []
    vpc_id_list.append(vpc_id)
    vpc.add_name_tag(vpc_id_list, vpc_name)

    print(f'Added {vpc_name} to {vpc_id}')

    # Create an IGW
    igw_response = vpc.create_internet_gateway()

    igw_id = igw_response['InternetGateway']['InternetGatewayId']

    vpc.attach_igw_to_vpc(vpc_id, igw_id)

    # Create public/private subnets
    zones = vpc.describe_availability_zones(region)

    subnet_ids_list = vpc.create_subnet(vpc_id, zones, number_of_subnets)
    public_subnet_id_list = subnet_ids_list[0:number_of_public_subnets]
    private_subnet_id_list = subnet_ids_list[number_of_public_subnets:number_of_subnets]

    print(f'Subnet(s) created for VPC {vpc_id} \nPublic Subnets: {public_subnet_id_list} \nPrivate Subnets: {private_subnet_id_list}')

    # Add name tag to Public/Private Subnets
    vpc.add_name_tag(public_subnet_id_list, 'Boto3-Public-Subnet')
    vpc.add_name_tag(private_subnet_id_list, 'Boto3-Private-Subnet')

    # Create a public route table
    public_route_table_id_list = vpc.create_public_route_table(vpc_id, number_of_public_subnets)

    # Adding the IGW to public route table
    vpc.create_igw_route_to_public_route_table(public_route_table_id_list, igw_id)

    # Associate Public Subnet with Route Table
    vpc.associate_subnet_with_route_table(public_subnet_id_list, public_route_table_id_list)

    

if __name__ == '__main__':
    main()