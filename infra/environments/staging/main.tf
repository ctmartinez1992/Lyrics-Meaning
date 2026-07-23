terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    key            = "lyrics-meaning/staging/terraform.tfstate"
    dynamodb_table = "terraform-state-locks"
  }
}

provider "aws" {
  region = var.aws_region
}

module "networking" {
  source               = "../../modules/networking"
  name_prefix          = "lyrics-meaning-staging"
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "iam" {
  source      = "../../modules/iam"
  name_prefix = "lyrics-meaning-staging"
}

module "secrets" {
  source            = "../../modules/secrets"
  name_prefix       = "lyrics-meaning-staging"
  django_secret_key = var.django_secret_key
  database_password = var.db_password
}

module "postgres" {
  source                = "../../modules/postgres"
  name_prefix           = "lyrics-meaning-staging"
  db_subnet_ids         = module.networking.private_subnet_ids
  db_security_group_ids = var.db_security_group_ids
  db_name               = var.db_name
  db_username           = var.db_username
  db_password           = var.db_password
}

module "app_runtime" {
  source                     = "../../modules/app_runtime"
  name_prefix                = "lyrics-meaning-staging"
  private_subnet_ids         = module.networking.private_subnet_ids
  service_security_group_ids = var.app_security_group_ids
}
