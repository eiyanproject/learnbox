# The two-tier VPC from foundations lesson 7, built for a lesson to use.
# What `eval "$(awslab given vpc)"` builds, written as the CLI commands it
# stands for (awslab does the same in one boto3 process, which is faster).
# Sets: VPC_ID PUBLIC_A PUBLIC_B PRIVATE_A PRIVATE_B IGW_ID PUBLIC_RT
_name() { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2}]"; }
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications "$(_name vpc lb-vpc)" --query Vpc.VpcId --output text)
_subnet() {  # name cidr az
  aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block "$2" --availability-zone "$3" \
    --tag-specifications "$(_name subnet "$1")" --query Subnet.SubnetId --output text
}
PUBLIC_A=$(_subnet public-a 10.0.1.0/24 us-east-1a)
PUBLIC_B=$(_subnet public-b 10.0.2.0/24 us-east-1b)
PRIVATE_A=$(_subnet private-a 10.0.11.0/24 us-east-1a)
PRIVATE_B=$(_subnet private-b 10.0.12.0/24 us-east-1b)
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "$(_name internet-gateway lb-igw)" \
  --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"
PUBLIC_RT=$(aws ec2 create-route-table --vpc-id "$VPC_ID" \
  --tag-specifications "$(_name route-table public)" --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id "$PUBLIC_RT" --destination-cidr-block 0.0.0.0/0 \
  --gateway-id "$IGW_ID" >/dev/null
for _s in "$PUBLIC_A" "$PUBLIC_B"; do
  aws ec2 associate-route-table --route-table-id "$PUBLIC_RT" --subnet-id "$_s" >/dev/null
  aws ec2 modify-subnet-attribute --subnet-id "$_s" --map-public-ip-on-launch
done
echo "given vpc: $VPC_ID (public $PUBLIC_A $PUBLIC_B, private $PRIVATE_A $PRIVATE_B)"
