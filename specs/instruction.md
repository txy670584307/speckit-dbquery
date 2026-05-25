# Instruction

## constitution
- 后端使用 Ergonomic Python 风格来编写代码，前端使用typescript
- 前后端都要有严格的类型标注
- 使用pydantic 来定义数据模型
- 所有后端生成的 JSON 数据，使用 camelCase 格式
- 不需要 authentication，任何用户都可以使用。

## 基本思路

这是一个数据库查询工具。用户可以添加一个db url,系统会连接到数据库，获取数据库的metadata，然后将数据库的table和view的信息展示出来，然后用户可以自己输入sql查询，也可以通过自然语言来生成查询。

基本想法:
- 数据库连接字符串和数据库的metadata都会存储到sqlite数据库中。我们可以根据postgres的功能

- 数据库连接字符串和数据库的metadata 都会存储到 sqlite 数据库中。我们可以根据 postgres的功能来查询系统中的表和视图的信息，然后用 LLM 来将这些信息转换成 json 格式，然后存储到 sqlite 数据库中。这个信息以后可以复用。
- 当用户使用LLM 来生成 sql查询时，我们可以把系统中的表和视图的信息作为Context 传递给 LLM，然后LLM 会根据这些信息来生成sql查询。
- 任何输入的 sql语句，都需要经过 sqlparser解析，确保语法正确，并且仅包含select 语句。如果语法不正确，需要给出错误信息.
    - 如果查询不包含limit 子句，默认添加limit 1000 语句。
- 输出格式是 json，前端将其组织成表格，并显示出来。

后端使用 Python(uv)/FastAPI/sqlglot
前端使用 vue2/vue-router/element-ui 来实现.
sql editor 使用 monaco editor 来实现

后端API需要支撑cors,允许所有origin访问.
后端API如下:
# 获取所有已连接的数据库
GET /api/v1/dbs

# 添加数据库连接
POST /api/v1/dbs/{db_name}
Request Body:
{
    "db_url": "jdbc:postgresql://localhost:5432/postgres?user=postgres&password=postgres"
}

# 获取数据库的metadata
GET /api/v1/dbs/{db_name}

# 查询某个数据的信息
POST /api/v1/dbs/{db_name}/query
Request Body:
{
    "sql": "select * from table_name"
}

# 根据自然语言生成sql查询
POST /api/v1/dbs/{db_name}/query/natural
Request Body:
{
    "natural": "查询所有用户"
}