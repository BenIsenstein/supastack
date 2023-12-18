name: Build and deploy to aws
on:
  push:
    branches:
      - ${RELEASE_BRANCH}
env:       
  VITE_SUPABASE_API_KEY: ${VITE_SUPABASE_API_KEY}
  VITE_SUPABASE_API_URL: ${VITE_SUPABASE_API_URL}
jobs:
  deploy:
    name: Upload to Amazon S3
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: ${RELEASE_BRANCH}
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${ASSUME_ROLE}
          aws-region: ${AWS_REGION}
      - name: Install and build
        run: |
          npm install && npm run build
      - name: Copy files to the test website with the AWS CLI
        run: |
          aws s3 sync dist s3://${WEB_BUCKET} --delete
