# Deployment Checklist for Integrations App

Use this checklist before deploying to production.

## Pre-Deployment

### Environment Configuration
- [ ] Generate new `SECRET_KEY` (never use default)
- [ ] Generate new `FIELD_ENCRYPTION_KEY` using Fernet
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Set up proper `DATABASE_URL` (PostgreSQL recommended)
- [ ] Configure `CORS_ALLOWED_ORIGINS` with frontend URL(s)
- [ ] Set `FRONTEND_URL` to production frontend
- [ ] Configure `SENDGRID_API_KEY` for production emails
- [ ] Set `DEFAULT_FROM_EMAIL` to your domain email

### Discord OAuth
- [ ] Create production Discord application
- [ ] Set `DISCORD_CLIENT_ID` from production app
- [ ] Set `DISCORD_CLIENT_SECRET` from production app
- [ ] Update `DISCORD_REDIRECT_URI` to production URL
- [ ] Add production redirect URI in Discord Developer Portal
- [ ] Test OAuth flow in production environment

### Redis & Celery
- [ ] Set up production Redis instance
- [ ] Configure `CELERY_BROKER_URL` with production Redis
- [ ] Configure `CELERY_RESULT_BACKEND` with production Redis
- [ ] Enable Redis authentication
- [ ] Configure Redis persistence (AOF/RDB)
- [ ] Set up Redis monitoring

### Database
- [ ] Run all migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Set up database backups
- [ ] Configure database connection pooling
- [ ] Enable database SSL if available

### Security
- [ ] Review all environment variables
- [ ] Ensure no secrets in version control
- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Configure CSRF settings
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Configure CORS properly
- [ ] Review file upload limits
- [ ] Set up firewall rules

## Deployment

### Application Server
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Configure WSGI server (Gunicorn/uWSGI)
- [ ] Set up process manager (Supervisor/systemd)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up SSL certificates (Let's Encrypt)

### Celery Workers
- [ ] Configure Celery worker service
- [ ] Configure Celery beat service
- [ ] Set appropriate concurrency levels
- [ ] Configure worker monitoring
- [ ] Set up automatic restarts
- [ ] Configure log rotation

### Monitoring & Logging
- [ ] Set up application logging
- [ ] Configure Celery logging
- [ ] Set up error tracking (Sentry)
- [ ] Configure performance monitoring
- [ ] Set up uptime monitoring
- [ ] Configure log aggregation
- [ ] Set up alerts for critical errors

### Testing
- [ ] Run all tests: `python manage.py test`
- [ ] Test Discord OAuth flow
- [ ] Test Telegram bot connection
- [ ] Test channel syncing
- [ ] Test token refresh
- [ ] Test health checks
- [ ] Load test API endpoints
- [ ] Test Celery tasks

## Post-Deployment

### Verification
- [ ] Verify all API endpoints are accessible
- [ ] Test user registration and login
- [ ] Test Discord OAuth connection
- [ ] Test Telegram bot connection
- [ ] Verify Celery workers are running
- [ ] Verify Celery beat is running
- [ ] Check scheduled tasks are executing
- [ ] Monitor error logs for issues

### Documentation
- [ ] Update API documentation
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures
- [ ] Create incident response plan

### Backup & Recovery
- [ ] Test database backup
- [ ] Test database restore
- [ ] Document recovery procedures
- [ ] Set up automated backups
- [ ] Test disaster recovery plan

## Maintenance

### Regular Tasks
- [ ] Monitor application logs daily
- [ ] Review Celery task failures
- [ ] Check Redis memory usage
- [ ] Monitor database performance
- [ ] Review security logs
- [ ] Update dependencies monthly
- [ ] Review and rotate secrets quarterly

### Performance Optimization
- [ ] Monitor API response times
- [ ] Optimize slow database queries
- [ ] Review Celery task performance
- [ ] Monitor Redis performance
- [ ] Optimize static file delivery
- [ ] Review and adjust caching

## Rollback Plan

If deployment fails:
1. [ ] Stop new application server
2. [ ] Revert to previous version
3. [ ] Restore database if needed
4. [ ] Restart Celery workers
5. [ ] Verify old version is working
6. [ ] Document what went wrong
7. [ ] Fix issues before retry

## Emergency Contacts

- **DevOps Lead**: [Contact Info]
- **Backend Lead**: [Contact Info]
- **Database Admin**: [Contact Info]
- **Security Team**: [Contact Info]

## Service URLs

- **Production API**: https://api.yourdomain.com
- **Admin Panel**: https://api.yourdomain.com/admin/
- **Celery Flower**: https://flower.yourdomain.com (if deployed)
- **Monitoring**: [Your monitoring URL]
- **Error Tracking**: [Your Sentry URL]

## Quick Commands

### Check Application Status
```bash
# Check if Django is running
curl https://api.yourdomain.com/api/v1/integrations/

# Check Celery worker
celery -A Infobyte inspect active

# Check Celery beat
celery -A Infobyte inspect scheduled
```

### Restart Services
```bash
# Restart Django (systemd)
sudo systemctl restart gunicorn

# Restart Celery worker
sudo systemctl restart celery-worker

# Restart Celery beat
sudo systemctl restart celery-beat

# Restart Redis
sudo systemctl restart redis
```

### View Logs
```bash
# Django logs
tail -f /var/log/gunicorn/error.log

# Celery worker logs
tail -f /var/log/celery/worker.log

# Celery beat logs
tail -f /var/log/celery/beat.log

# Redis logs
tail -f /var/log/redis/redis-server.log
```

### Database Operations
```bash
# Create backup
pg_dump dbname > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql dbname < backup_file.sql

# Run migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## Made with Bob