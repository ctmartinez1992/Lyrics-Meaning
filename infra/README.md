# Terraform layout

## Modules
- `modules/networking`: VPC and subnets
- `modules/app_runtime`: ECS cluster and CloudWatch logging/alarms baseline
- `modules/postgres`: RDS PostgreSQL instance
- `modules/iam`: task roles
- `modules/secrets`: Secrets Manager entries for Django and DB credentials

## Environment stacks
- `environments/dev`
- `environments/staging`
- `environments/prod`

Each stack uses a dedicated S3 backend key:
- `lyrics-meaning/dev/terraform.tfstate`
- `lyrics-meaning/staging/terraform.tfstate`
- `lyrics-meaning/prod/terraform.tfstate`

All stacks share the DynamoDB lock table `terraform-state-locks`.

## Usage
1. `cd infra/environments/<env>`
2. Configure backend bucket and variables.
3. `terraform init`
4. `terraform plan -var-file=terraform.tfvars`
5. `terraform apply -var-file=terraform.tfvars`
