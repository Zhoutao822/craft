
# Room时间属性支持



```kotlin
@Entity(tableName = "users")
data class User(
        @PrimaryKey val id: Long? = null,
        val username: String,
        val joined_date: OffsetDateTime? = null
)
```

```kotlin
object TiviTypeConverters {
    private val formatter = DateTimeFormatter.ISO_OFFSET_DATE_TIME

    @TypeConverter
    @JvmStatic
    fun toOffsetDateTime(value: String?): OffsetDateTime? {
        return value?.let {
            return formatter.parse(value, OffsetDateTime::from)
        }
    }

    @TypeConverter
    @JvmStatic
    fun fromOffsetDateTime(date: OffsetDateTime?): String? {
        return date?.format(formatter)
    }
}
```

`2013-10-07T17:23:19.540-04:00`等价于`7th October 2013, 17:23:19.540 UTC-4`

考虑时区排序

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY datetime(joined_date)")
    fun getOldUsers(): List<User>
}
```
