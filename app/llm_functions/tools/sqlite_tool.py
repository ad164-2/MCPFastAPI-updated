"""
SQLite Tool - Execute SQLite queries on the application database
"""

import sqlite3
from typing import Any, Dict, List
from app.mcp.base_tool import BaseTool



class Sqlite(BaseTool):
    """Tool to execute SQLite queries"""

    async def execute(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Execute a SQLite query
        
        Args:
            query: SQL query to execute
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with query results
        """
        try:
            db_path = self.config.get("DB_PATH", "./my_database.db")
            timeout = self.config.get("TIMEOUT", 30)
            max_results = self.config.get("MAX_RESULTS", 100)
            
            # Enforce limit
            actual_limit = min(limit, max_results)
            
            # Add LIMIT clause if not present and it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                if "LIMIT" not in query.upper():
                    query += f" LIMIT {actual_limit}"
            
            logger.info(f"Executing SQLite query: {query[:100]}...")
            
            conn = sqlite3.connect(db_path, timeout=timeout)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query)
            
            # For SELECT queries, fetch results
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                
                conn.close()
                
                return {
                    "success": True,
                    "rows_affected": len(results),
                    "data": results,
                    "query": query
                }
            else:
                # For INSERT, UPDATE, DELETE queries
                conn.commit()
                rows_affected = cursor.rowcount
                conn.close()
                
                return {
                    "success": True,
                    "rows_affected": rows_affected,
                    "data": None,
                    "query": query
                }
            
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
        except Exception as e:
            logger.error(f"Error executing SQLite query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def get_schema(self) -> Dict[str, Any]:
        """Get input schema for Sqlite tool"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT, INSERT, UPDATE, DELETE)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (for SELECT queries)",
                    "default": 100
                }
            },
            "required": ["query"]
        }
