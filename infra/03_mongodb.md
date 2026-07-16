## quick reference
```javascript
// show all databases
show dbs

// switch to db
use kb

// show collections in current db
show collections

// insert document into collection
db.kb.insertOne({})
db.kb.insertMany([])

// find all documents in collection
db.kb.find()

// find document by filter
db.users.find({name: "张三"})
db.users.find({ age: { $gt: 25 } })
db.users.find({ city: "Beijing", age: { $lte: 30 } })
db.users.find({ $or: [ { city: "Beijing" }, { age: { $gt: 30 } } ] })
db.users.find({ age: { $in: [25, 30] } })

// update document
db.users.updateOne({ name: "张三" }, { $set: { age: 26 } })
db.users.updateMany({ city: "Beijing" }, { $set: { status: "active" } })
db.users.updateOne({ name: "李四" }, { $inc: { age: 1 } })

// delete document
db.users.deleteOne({ name: "王五" })
db.users.deleteOne({ age: { $gte: 35 } })
```

## connect to mongodb docker container and run mongosh
```bash
[root@localhost ~]# docker exec -it mongo mongosh
Current Mongosh Log ID: 6a57a7e09a11aac56fd805da
Connecting to:          mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.8.1
Using MongoDB:          8.2.6
Using Mongosh:          2.8.1

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/

------
   The server generated these startup warnings when booting
   2026-07-15T00:50:08.549+00:00: Access control is not enabled for the database. Read and write access to data and configuration is unrestricted
   2026-07-15T00:50:08.550+00:00: For customers running the current memory allocator, we suggest changing the contents of the following sysfsFile
   2026-07-15T00:50:08.550+00:00: We suggest setting the contents of sysfsFile to 0.
   2026-07-15T00:50:08.550+00:00: vm.max_map_count is too low
   2026-07-15T00:50:08.550+00:00: We suggest setting swappiness to 0 or 1, as swapping can cause performance problems.
------

test>
```

## show databases
```bash
test> show dbs
admin   40.00 KiB
config  36.00 KiB
local   68.00 KiB
```

## switch to database
```bash
test> use local
switched to db local
```

## show collections/tables
```bash
local> show collections
startup_log

local> db.startup_log.find()
[
  {
    _id: 'bfd444b92340-1783415281234',
    hostname: 'bfd444b92340',
    startTime: ISODate('2026-07-07T09:08:01.000Z'),
    startTimeLocal: 'Tue Jul  7 09:08:01.234',
    cmdLine: { net: { bindIp: '*' } },
    pid: Long('1'),
    buildinfo: {
      version: '8.2.6',
      versionArray: [ 8, 2, 6, 0 ],
      gitVersion: '5d25c835745d06f712320b6cdae9d50b7b43663e',
      modules: [],
      allocator: 'tcmalloc-google',
      javascriptEngine: 'mozjs',
      sysinfo: 'deprecated',
      openssl: {
        running: 'OpenSSL 3.0.13 30 Jan 2024',
        compiled: 'OpenSSL 3.0.13 30 Jan 2024'
      },
      buildEnvironment: {
        ...
      },
      bits: 64,
      debug: false,
      maxBsonObjectSize: Long('16777216'),
      storageEngines: [ 'devnull', 'wiredTiger' ]
    }
  },
  ...
]
```

## insert document into collection
```bash
local> use kb
switched to db kb

kb> db.users.insertOne({ name: "张三", age: 25, email: "zhangsan@example.com" })
{
  acknowledged: true,
  insertedId: ObjectId('6a57aa189a11aac56fd805db')
}

kb> db.users.find()
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 25,
    email: 'zhangsan@example.com'
  }
]

kb> db.users.insertMany([
|   { name: "李四", age: 30, email: "lisi@example.com", city: "Beijing" },
|   { name: "王五", age: 28, email: "wangwu@example.com", city: "Shanghai" },
|   { name: "赵六", age: 35, email: "zhaoliu@example.com", city: "Beijing" }
| ])
{
  acknowledged: true,
  insertedIds: {
    '0': ObjectId('6a57b3e09a11aac56fd805dc'),
    '1': ObjectId('6a57b3e09a11aac56fd805dd'),
    '2': ObjectId('6a57b3e09a11aac56fd805de')
  }
}
```

## find documents in collection
```bash
kb> db.users.find()
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 25,
    email: 'zhangsan@example.com'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 30,
    email: 'lisi@example.com',
    city: 'Beijing'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dd'),
    name: '王五',
    age: 28,
    email: 'wangwu@example.com',
    city: 'Shanghai'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805de'),
    name: '赵六',
    age: 35,
    email: 'zhaoliu@example.com',
    city: 'Beijing'
  }
]

kb> db.users.find({name: "张三"})
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 25,
    email: 'zhangsan@example.com'
  }
]

b> db.users.find({ age: { $gt: 25 } })
[
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 30,
    email: 'lisi@example.com',
    city: 'Beijing'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dd'),
    name: '王五',
    age: 28,
    email: 'wangwu@example.com',
    city: 'Shanghai'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805de'),
    name: '赵六',
    age: 35,
    email: 'zhaoliu@example.com',
    city: 'Beijing'
  }
]

kb> db.users.find({ city: "Beijing", age: { $lte: 30 } })
[
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 30,
    email: 'lisi@example.com',
    city: 'Beijing'
  }
]

kb> db.users.find({ $or: [ { city: "Beijing" }, { age: { $gt: 30 } } ] })
[
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 30,
    email: 'lisi@example.com',
    city: 'Beijing'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805de'),
    name: '赵六',
    age: 35,
    email: 'zhaoliu@example.com',
    city: 'Beijing'
  }
]

kb> db.users.find({ age: { $in: [25, 30] } })
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 25,
    email: 'zhangsan@example.com'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 30,
    email: 'lisi@example.com',
    city: 'Beijing'
  }
]
```

## update
```bash
kb> db.users.updateOne({ name: "张三" }, { $set: { age: 26 } })
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}

kb> db.users.updateMany({ city: "Beijing" }, { $set: { status: "active" } })
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 2,
  modifiedCount: 2,
  upsertedCount: 0
}

kb> db.users.updateOne({ name: "李四" }, { $inc: { age: 1 } })
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}

kb> db.users.find()
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 26,
    email: 'zhangsan@example.com'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 31,
    email: 'lisi@example.com',
    city: 'Beijing',
    status: 'active'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dd'),
    name: '王五',
    age: 28,
    email: 'wangwu@example.com',
    city: 'Shanghai'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805de'),
    name: '赵六',
    age: 35,
    email: 'zhaoliu@example.com',
    city: 'Beijing',
    status: 'active'
  }
]
```

## delete document from collection
```bash
kb> db.users.deleteOne({ name: "王五" })
{ acknowledged: true, deletedCount: 1 }

kb> db.users.find()
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 26,
    email: 'zhangsan@example.com'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 31,
    email: 'lisi@example.com',
    city: 'Beijing',
    status: 'active'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805de'),
    name: '赵六',
    age: 35,
    email: 'zhaoliu@example.com',
    city: 'Beijing',
    status: 'active'
  }
]

kb> db.users.deleteOne({ age: { $gte: 35 } })
{ acknowledged: true, deletedCount: 1 }

kb> db.users.find()
[
  {
    _id: ObjectId('6a57aa189a11aac56fd805db'),
    name: '张三',
    age: 26,
    email: 'zhangsan@example.com'
  },
  {
    _id: ObjectId('6a57b3e09a11aac56fd805dc'),
    name: '李四',
    age: 31,
    email: 'lisi@example.com',
    city: 'Beijing',
    status: 'active'
  }
]
```