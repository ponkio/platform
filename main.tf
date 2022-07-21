provider "aws" {
    region = "us-east-2"
}

module "ecs" {
    cluster_name = "le_producer"

    cluster_configuratoin = {
        
    }
}