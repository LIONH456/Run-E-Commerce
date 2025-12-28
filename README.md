# MiniShop (E-Commerce Demo)

This single-file guide contains everything to run and deploy the MiniShop project (Django + MySQL + Gunicorn + Nginx) locally and on AWS EC2. The project implements the requirements in `re-exam.md` (product listing, detail, cart, checkout as guest, admin product management, orders and order items).

---

## Quick project structure

- `minishop/` — Django project
- `store/` — Django app (models: Product, Order, OrderItem)
- `templates/` — HTML templates
- `Dockerfile`, `docker-compose.yml` — local dev & container configuration, includes MySQL service
- `compose/nginx.conf` — Nginx to proxy to Gunicorn and serve static files
- `db/init.sql` — sample product data imported into MySQL on first run

---

## Prerequisites (local)

- Git, Docker & Docker Compose OR Python 3.11 and MySQL server
- (If running without Docker) Create a Python virtualenv and install packages from `requirements.txt`

---

## Local: Run with Docker (recommended)

1. Clone the repo:
   git clone <your-repo> && cd minishop

2. (Optional) Change DB credentials in `docker-compose.yml` or set envs in a `.env` file. Make sure to copy `.env.example` to `.env` and never commit your real `.env` file with secrets to Git.

3. Build and start (this creates a MySQL container, imports sample data, and starts Django app + Nginx):
   docker-compose up --build

4. Visit: http://localhost

5. Admin: create superuser inside the `web` container:
   docker-compose exec web python manage.py createsuperuser
   Then go to http://localhost/admin and manage products.

Notes:
- MySQL is available at host `db` inside containers; for local tools you can connect to `localhost:3306`.
- The initializer `db/init.sql` seeds two products. Adjust or add SQL there for more items.

---

## Local: Run without Docker (connect to local MySQL)

1. Install dependencies:
   python -m venv venv
   venv\Scripts\activate  (Windows)
   pip install -r requirements.txt

2. Create a `.env` file in project root with content:
   DJANGO_SECRET_KEY=you_should_change
   DEBUG=1
   DB_NAME=minishop
   DB_USER=minishop
   DB_PASSWORD=minishop_password
   DB_HOST=127.0.0.1
   DB_PORT=3306

3. Create MySQL database and user (example):
   CREATE DATABASE minishop;
   CREATE USER 'user1'@'localhost' IDENTIFIED BY 'minishop_password';
   GRANT ALL PRIVILEGES ON minishop.* TO 'minishop'@'localhost';

4. Run migrations and start server:
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver

5. Visit: http://127.0.0.1:8000

---

## Deploy to AWS EC2 (beginner-friendly step-by-step)

1. Create a free-tier EC2 instance (Ubuntu 22.04 recommended).
   - In AWS Console > EC2 > Launch Instance > choose Ubuntu Server.
   - Choose t2.micro or t3.micro (free-tier eligible).
   - Configure Security Group: allow inbound ports 22 (SSH), 80 (HTTP), and 3306 only if you need remote DB access (avoid exposing DB publicly if possible).

2. SSH into your instance:
   ssh -i path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>

3. Install Docker and Docker Compose:
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker $USER
   # log out and back in or use newgrp docker

4. Clone repo to server:
   git clone <your-repo>
   cd minishop

5. Copy `.env` to server with secure values (set DJANGO_SECRET_KEY, DB passwords, DEBUG=0):
   cat > .env <<EOF
   DJANGO_SECRET_KEY=change_this_secret
   DEBUG=0
   DB_NAME=minishop
   DB_USER=minishop
   DB_PASSWORD=minishop_password
   DB_HOST=db
   DB_PORT=3306
   EOF

6. Start containers:
   sudo docker-compose up -d --build

7. Check services:
   sudo docker ps
   # Logs
   sudo docker-compose logs -f web

8. Visit http://<EC2_PUBLIC_IP> to see the site.

9. (Optional) Add a domain and point an A record to the EC2 public IP.

10. Secure production:
   - Use HTTPS (Certbot or load balancer) — For a beginner, consider using AWS Certificate Manager + CloudFront or configure certbot with Nginx and obtain certificates.
   - Protect DB by restricting access to only the server or moving to RDS.

### Domain / Nginx notes (quick)
- Point your domain to the EC2 public IP with an A record (e.g., `@` and `www`).
- Update `compose/nginx.conf` `server_name` line to use your domain and redeploy `docker-compose up -d --build`.
- Open ports 80 and 443 in your instance security group (EC2) and port 80 if you will add certs.
- For HTTPS: on the server you can use certbot (Let's Encrypt) to obtain certs and configure Nginx. Alternatively use AWS Certificate Manager + CloudFront if you prefer a managed TLS solution.

Example minimal Nginx steps on EC2 (if you use the nginx container from `docker-compose`):
1) Edit `compose/nginx.conf`, set `server_name yourdomain.com;` and map static location correctly (already configured in compose to mount `./staticfiles:/static`).
2) Restart nginx container: `docker-compose restart nginx`.
3) Obtain TLS: use certbot on the host (with Nginx stopped) or use Dockerized certbot solutions – see https://certbot.eff.org for detailed steps.

If you want, I can prepare a `prod-nginx.conf` file with an SSL/redirect template and a short certbot recipe for Ubuntu on EC2.

---

## Notes & reminders

- Admin pages fulfill the admin requirement from `re-exam.md` (list, add, edit, delete via Django admin).
- Orders are stored in DB along with order items; guest checkout implemented via simple form.
- For production, turn off DEBUG, set a strong `DJANGO_SECRET_KEY`, and configure proper static/media serving and HTTPS.

### Troubleshooting: "Table ... doesn't exist"
If you see an error like: `(1146, "Table 'minishop.store_product' doesn't exist")` when loading the site, it means the database exists but Django tables were not created yet. Fix it locally by running:

1. Ensure your database settings are correct in `.env` and the DB server is running.
2. Run migrations:
   - python manage.py makemigrations store
   - python manage.py migrate

If you prefer the migration files already present, you can simply run:
   - python manage.py migrate

If you use Docker, `docker-compose up` runs migrations automatically via the container entrypoint, or run:
   docker-compose exec web python manage.py migrate

If you still have problems, check DB connectivity and user privileges (DB name, user, password and host/port).

### Troubleshooting: "I have data in MySQL but it doesn't show on the site"
If your database already contains a legacy `products` table (created by an earlier script) and its rows don't show up on the site, it's because Django's `Product` model uses the `store_product` table name by default.

To resolve this automatically I added a data migration (`store/migrations/0002_import_legacy_products.py`) that will copy rows from the legacy `products` table into `store_product` the first time you run `migrate` (only if `store_product` is empty).

If you already ran migrations before this migration was added, run again:
   - python manage.py migrate

If your data still does not appear, check the following:
- Confirm the `products` table exists and has rows:
   - Use your MySQL client: `SELECT COUNT(*) FROM products;`
- Confirm Django is connected to the same MySQL instance (check `.env` DB_HOST, DB_PORT, DB_NAME)
- If necessary, export and import the data manually or run the SQL shown above to copy rows into `store_product`.

---

## If you want me to: ✅
- Create a GitHub repo and push (I can supply Git commands)
- Create a small deployment script for EC2 (systemd service + docker-compose)

---

Enjoy! If you'd like, I can now add unit tests or create the GitHub repo and push the code for you.