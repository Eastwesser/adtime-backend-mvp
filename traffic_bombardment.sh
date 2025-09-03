#!/bin/bash

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting API Traffic Bombardment!${NC}"
echo -e "${BLUE}This will generate realistic traffic patterns...${NC}"

while true; do
    # Random delay between requests (1-5 seconds)
    sleep $((1 + RANDOM % 5))
    
    # Randomly choose an endpoint category
    case $((RANDOM % 10)) in
        0) # Authentication (15% chance)
            case $((RANDOM % 5)) in
                0) curl -s http://localhost:8042/api/v1/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"test"}' ;;
                1) curl -s http://localhost:8042/api/v1/auth/register -X POST -H "Content-Type: application/json" -d '{"email":"user'$RANDOM'@test.com","password":"test123"}' ;;
                2) curl -s http://localhost:8042/api/v1/auth/refresh -X POST ;;
                3) curl -s http://localhost:8042/api/v1/auth/logout -X POST ;;
                4) curl -s http://localhost:8042/api/v1/auth/check-email -X POST -H "Content-Type: application/json" -d '{"email":"check'$RANDOM'@test.com"}' ;;
            esac
            echo -e "${GREEN}🔐 Auth request completed${NC}" ;;
            
        1) # Users (10% chance)
            curl -s http://localhost:8042/api/v1/users/me
            echo -e "${BLUE}👤 User request completed${NC}" ;;
            
        2) # Marketplace (15% chance)
            case $((RANDOM % 4)) in
                0) curl -s http://localhost:8042/api/v1/marketplace/items ;;
                1) curl -s http://localhost:8042/api/v1/marketplace/items/1/cart -X POST ;;
                2) curl -s http://localhost:8042/api/v1/marketplace/items/1/order -X POST ;;
                3) curl -s http://localhost:8042/api/v1/marketplace/orders/direct -X POST -H "Content-Type: application/json" -d '{"item_id":1,"quantity":1}' ;;
            esac
            echo -e "${YELLOW}🏪 Marketplace request completed${NC}" ;;
            
        3) # Orders (15% chance)
            case $((RANDOM % 3)) in
                0) curl -s http://localhost:8042/api/v1/orders ;;
                1) curl -s http://localhost:8042/api/v1/orders/1 ;;
                2) curl -s http://localhost:8042/api/v1/orders/1/messages ;;
            esac
            echo -e "${BLUE}📦 Order request completed${NC}" ;;
            
        4) # Payments (10% chance)
            curl -s http://localhost:8042/api/v1/payment/create -X POST -H "Content-Type: application/json" -d '{"amount":100,"currency":"RUB"}'
            echo -e "${GREEN}💳 Payment request completed${NC}" ;;
            
        5) # Generations (15% chance)
            case $((RANDOM % 3)) in
                0) curl -s http://localhost:8042/api/v1/generate -X POST -H "Content-Type: application/json" -d '{"prompt":"beautiful landscape"}' ;;
                1) curl -s http://localhost:8042/api/v1/generate/1/status ;;
                2) curl -s http://localhost:8042/api/v1/generate/1/cancel -X POST ;;
            esac
            echo -e "${YELLOW}🎨 Generation request completed${NC}" ;;
            
        6) # System endpoints (10% chance)
            case $((RANDOM % 4)) in
                0) curl -s http://localhost:8042/health ;;
                1) curl -s http://localhost:8042/metrics ;;
                2) curl -s http://localhost:8042/docs ;;
                3) curl -s http://localhost:8042/openapi.json ;;
            esac
            echo -e "${BLUE}🖥️  System request completed${NC}" ;;
            
        7) # Admin endpoints (5% chance - rare!)
            if [ $((RANDOM % 20)) -eq 0 ]; then
                curl -s http://localhost:8042/api/v1/admin/generations/stats
                echo -e "${RED}👑 Admin request completed${NC}"
            fi ;;
            
        8) # Errors on purpose! (5% chance)
            curl -s http://localhost:8042/nonexistent-endpoint
            curl -s http://localhost:8042/api/v1/invalid-route
            echo -e "${RED}❌ Error request (on purpose)${NC}" ;;
            
        9) # OAuth and other endpoints (10% chance)
            curl -s http://localhost:8042/api/v1/oauth/providers
            curl -s http://localhost:8042/api/v1/balance
            echo -e "${GREEN}🔗 OAuth/Balance request completed${NC}" ;;
    esac
    
    # Occasionally print status
    if [ $((RANDOM % 50)) -eq 0 ]; then
        echo -e "${YELLOW}📊 Still bombarding... Check Grafana for beautiful graphs!${NC}"
    fi
done