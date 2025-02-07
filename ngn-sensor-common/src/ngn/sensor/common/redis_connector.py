import json
import logging

from redis import ConnectionPool, Redis, exceptions

log = logging.getLogger(__name__)


class RedisConnector:
    def __init__(self, host: str = "redis", port: int = 6379, db_index: int = 0):
        """Initialises the RedisConnector and establishes a connection to the Redis server.

        Args:
            host (str): The hostname or IP address of the Redis server.
            port (int): The port number of the Redis server.
            db_index (int): The Redis database index to use.
        """

        self._connection_pool = ConnectionPool(host=host, port=port, db=db_index)
        self._redis_client = Redis(
            connection_pool=self._connection_pool, decode_responses=True
        )
        self._connect()

    def _connect(self):
        """
        Establishes a connection to the Redis server.
        """

        log.info("Connecting to Redis...")

        try:
            self._redis_client.ping()
        except exceptions.ConnectionError as e:
            log.error("Failed to connect to Redis: %s", e)
        else:
            log.info("Connection to Redis successful")

    def store(
        self, key: str, value, ex: int = None, nx: bool = None, xx: bool = None
    ) -> bool:
        """Sets the value of a key.

        Args:
            key (str): The key to set.
            value (any): The value to set.
            ex (int): Expiration time in seconds.
            nx (bool): Set the value only if the key does not exist.
            xx (bool): Set the value only if the key already exists.

        Returns:
            bool: whether or not the store operation was successful.
        """

        stored_successfully = False

        try:
            json_value = json.dumps(value)
            self._redis_client.set(name=key, value=json_value, ex=ex, nx=nx, xx=xx)
        except (exceptions.ConnectionError, exceptions.RedisError) as e:
            log.error("Error publishing data to Redis: %s", e)
        except TypeError as e:
            log.error("Error serialising '%s': %s", value, e)
        else:
            log.debug("Data stored correctly in Redis")
            stored_successfully = True

        return stored_successfully

    def get(self, key: str) -> dict:
        """
        Retrieves the value of a given key.

        Args:
            key (str): The key to retrieve.

        Returns:
            The value associated with the key, or None if the key does not exist.
        """

        value = None

        try:
            json_data = self._redis_client.get(name=key)
            if json_data:
                value: dict = json.loads(json_data)
                log.debug("Retrieved data %s from key %s", value, key)
            else:
                log.debug("Key %s not found in cache", key)
        except (exceptions.ConnectionError, exceptions.RedisError) as e:
            log.error("Error consuming data from Redis: %s", e)
        except TypeError as e:
            log.error("Error serialising '%s': %s", json_data, e)

        return value

    def delete(self, key: str):
        """
        Deletes a key.

        Args:
            key (str): The key to delete.
        """

        try:
            self._redis_client.delete(key)
        except (exceptions.ConnectionError, exceptions.RedisError) as e:
            log.error("Error deleting data from Redis: %s", e)
        else:
            log.debug("Data with key %s deleted successfully", key)

    def exists(self, key):
        """
        Checks if a key exists.

        Args:
            key (str): The key to check.

        Returns:
            True if the key exists, False otherwise.
        """

        return self._redis_client.exists(key)

    def expire(self, key: str, timeout):
        """
        Sets an expiration time for a key.

        Args:
            key (str): The key to set the expiration time for.
            timeout (int): Expiration time in seconds.
        """

        self._redis_client.expire(key, timeout)

    def close(self):
        """
        Closes the connection to the Redis server.
        """

        self._redis_client.close()
