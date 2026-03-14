import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');
const orderDuration = new Trend('order_duration');

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 100 },  // Ramp up to 100 users (spike)
    { duration: '2m', target: 50 },   // Ramp down to 50 users
    { duration: '1m', target: 10 },   // Ramp down to 10 users
    { duration: '1m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate should be less than 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test users (pre-registered)
const testUsers = [
  { username: 'user1', password: 'password123' },
  { username: 'user2', password: 'password123' },
  { username: 'user3', password: 'password123' },
];

let authTokens = {};

export function setup() {
  // Register test users and get tokens
  console.log('Setting up test users...');
  
  testUsers.forEach((user, index) => {
    // Register user
    const registerRes = http.post(`${BASE_URL}/api/v1/auth/register`, JSON.stringify({
      username: user.username,
      email: `user${index + 1}@test.com`,
      password: user.password,
      full_name: `Test User ${index + 1}`
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (registerRes.status === 201 || registerRes.status === 400) {
      // Login to get token
      const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
        username: user.username,
        password: user.password
      }), {
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (loginRes.status === 200) {
        const tokenData = JSON.parse(loginRes.body);
        authTokens[user.username] = tokenData.access_token;
        console.log(`User ${user.username} authenticated`);
      }
    }
  });
  
  // Create some test products
  const adminToken = authTokens[testUsers[0].username];
  if (adminToken) {
    for (let i = 1; i <= 10; i++) {
      http.post(`${BASE_URL}/api/v1/products`, JSON.stringify({
        name: `Product ${i}`,
        description: `Test product ${i}`,
        price: 10.99 * i,
        stock_quantity: 100,
        category: `Category ${(i % 3) + 1}`
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
      });
    }
  }
  
  return { tokens: authTokens };
}

export default function (data) {
  const userIndex = Math.floor(Math.random() * testUsers.length);
  const user = testUsers[userIndex];
  const token = data.tokens[user.username];
  
  if (!token) {
    console.error(`No token for user ${user.username}`);
    return;
  }
  
  // Test 1: Login (occasionally)
  if (Math.random() < 0.1) {
    const loginStart = Date.now();
    const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
      username: user.username,
      password: user.password
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    const loginTime = Date.now() - loginStart;
    loginDuration.add(loginTime);
    
    check(loginRes, {
      'login status is 200': (r) => r.status === 200,
    }) || errorRate.add(1);
    
    sleep(0.5);
  }
  
  // Test 2: List products
  const productsRes = http.get(`${BASE_URL}/api/v1/products?limit=20`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  check(productsRes, {
    'products status is 200': (r) => r.status === 200,
    'products has data': (r) => JSON.parse(r.body).length > 0,
  }) || errorRate.add(1);
  
  sleep(0.5);
  
  // Test 3: Get single product
  const productId = Math.floor(Math.random() * 10) + 1;
  const productRes = http.get(`${BASE_URL}/api/v1/products/${productId}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  check(productRes, {
    'product status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(0.5);
  
  // Test 4: Create order (occasionally)
  if (Math.random() < 0.3) {
    const orderStart = Date.now();
    const orderRes = http.post(`${BASE_URL}/api/v1/orders`, JSON.stringify({
      items: [
        {
          product_id: Math.floor(Math.random() * 10) + 1,
          quantity: Math.floor(Math.random() * 5) + 1,
          price: 10.99
        }
      ],
      shipping_address: '123 Test Street, Test City'
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
    });
    
    const orderTime = Date.now() - orderStart;
    orderDuration.add(orderTime);
    
    check(orderRes, {
      'order status is 201': (r) => r.status === 201,
    }) || errorRate.add(1);
    
    sleep(1);
  }
  
  // Test 5: List orders
  const ordersRes = http.get(`${BASE_URL}/api/v1/orders?limit=10`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  check(ordersRes, {
    'orders status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);
}

export function teardown(data) {
  console.log('Load test completed');
}


