// sh.enableSharding("TestDatabase")

// db.adminCommand( { shardCollection: "TestDatabase.TestCollection", key: { oemNumber: "hashed", zipCode: 1, supplierId: 1 }, numInitialChunks: 3 } )

sh.enableSharding("stock_data")
db.adminCommand( { shardCollection: "stock_data.tesla", key: { oemNumber: "hashed", zipCode: 1, supplierId: 1 }, numInitialChunks: 3 } )

sh.enableSharding("tweet_data")
db.adminCommand( { shardCollection: "tweet_data.elon_musk", key: { oemNumber: "hashed", zipCode: 1, supplierId: 1 }, numInitialChunks: 3 } )
db.adminCommand( { shardCollection: "tweet_data.elon_musk_important_tweets", key: { oemNumber: "hashed", zipCode: 1, supplierId: 1 }, numInitialChunks: 3 } )