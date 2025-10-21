"""
Test cases for static file serving and frontend functionality.
"""

import pytest
from fastapi import status


class TestStaticFiles:
    """Test cases for static file serving."""
    
    def test_static_index_html_accessible(self, client):
        """Test that static/index.html is accessible."""
        response = client.get("/static/index.html")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        
        # Check that it contains expected HTML elements
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "Mergington High School" in content
        assert "Extracurricular Activities" in content
    
    def test_static_css_accessible(self, client):
        """Test that static CSS files are accessible."""
        response = client.get("/static/styles.css")
        assert response.status_code == status.HTTP_200_OK
        assert "text/css" in response.headers["content-type"]
        
        # Check for some expected CSS content
        content = response.text
        assert "box-sizing" in content
        assert "activity-card" in content
    
    def test_static_js_accessible(self, client):
        """Test that static JavaScript files are accessible."""
        response = client.get("/static/app.js")
        assert response.status_code == status.HTTP_200_OK
        assert "javascript" in response.headers["content-type"] or "text/plain" in response.headers["content-type"]
        
        # Check for some expected JavaScript content
        content = response.text
        assert "fetchActivities" in content or "fetch" in content
        assert "addEventListener" in content
    
    def test_static_nonexistent_file_returns_404(self, client):
        """Test that requesting non-existent static files returns 404."""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == status.HTTP_404_NOT_FOUND