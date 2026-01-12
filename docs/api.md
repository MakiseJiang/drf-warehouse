# API 文档

## 资源

- `materials` 物料资源

## 端点

- `GET /api/materials/` 列出物料，支持分页与搜索
- `POST /api/materials/` 创建物料
- `GET /api/materials/<id>/` 获取单个物料
- `PUT /api/materials/<id>/` 完整更新物料
- `PATCH /api/materials/<id>/` 局部更新物料
- `DELETE /api/materials/<id>/` 删除物料

## 查询参数

- `page` 分页页码，从 1 开始
- `search` 文本搜索，按 `material_id、name、model_number、category、equipment、warehouse、shelf` 匹配

## 示例

### 列出物料

```
curl "http://127.0.0.1:8000/api/materials/?page=1"
```

### 搜索物料

```
curl "http://127.0.0.1:8000/api/materials/?search=M100"
```

### 创建物料

```
curl -X POST "http://127.0.0.1:8000/api/materials/" \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": "M200",
    "name": "Washer",
    "model_number": "W-1",
    "category": "Hardware",
    "equipment": "Motor",
    "warehouse": "WH2",
    "shelf": "B1",
    "quantity": 50
  }'
```