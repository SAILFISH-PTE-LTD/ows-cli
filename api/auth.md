# Auth 认证接口

Base: `https://api.ows.us`
统一响应: `{"code": 200, "message": "", "data": {...}}`

---

## POST /console/auth/getToken — 获取 Token

使用 app_id 和 app_secret 获取 access_token，1 分钟内最多调用 2 次。

**请求参数 (Query):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| appid | string | 是 | App ID |
| app_secret | string | 是 | App Secret |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| token_type | string | 类型（如 Bearer） |
| expires_in | int | 过期秒数，默认 7200 |
| access_token | string | Access Token |
| refresh_token | string | Refresh Token（7 天有效） |

---

## POST /console/auth/refreshToken — 刷新 Token

**请求参数 (Query):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | 是 | Refresh Token |

**响应 data:**

| 字段 | 类型 | 说明 |
|------|------|------|
| token_type | string | 类型 |
| access_token | string | 新 Access Token |
| refresh_token | string | 新 Refresh Token |
