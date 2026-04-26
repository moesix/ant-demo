"""
E2E Tests with Playwright
"""

from playwright.sync_api import Playwright, sync_playwright, expect

import os

def get_base_url():
    """Get the base URL for the application based on the environment"""
    # Check if we're running inside a Docker container
    if os.path.exists("/.dockerenv") or "DOCKER_CONTAINER" in os.environ:
        return "http://webapp:5000"
    else:
        return "http://localhost:5001"

def test_health_check_endpoint(playwright: Playwright):
    """Test the health check endpoint with Playwright"""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        response = page.goto(f"{get_base_url()}/health")
        assert response is not None
        assert response.status == 200
        
        # Check response contains healthy status
        assert "healthy" in page.content()
        assert "version" in page.content()
        
    finally:
        context.close()
        browser.close()

def test_application_rendering_and_behavior(playwright: Playwright):
    """Test application rendering and behavior with Playwright"""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        response = page.goto(f"{get_base_url()}/")
        assert response is not None
        assert response.status == 200

        # Check for main components
        expect(page.locator("h1.logo")).to_contain_text("antdemo")
        expect(page.locator(".tagline")).to_contain_text("Kubernetes Cluster Application Showcase")
        expect(page.locator(".version-badge")).to_contain_text("v3")

        # Check for application output
        expect(page.locator(".content-output")).to_contain_text("Your access has been logged to PGSQL.")

        # Check for system information section or access logs
        # Depending on the APP_VERSION, we might see either system metrics or access logs
        if page.locator(".system-metrics").is_visible():
            expect(page.locator(".metric-card")).to_have_count(5)
        if page.locator(".logs-container").is_visible():
            expect(page.locator(".log-item")).not_to_have_count(0)
        
    finally:
        context.close()
        browser.close()

def test_navigation_and_links(playwright: Playwright):
    """Test navigation and links are working"""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto(f"{get_base_url()}/")

        # Test health check link
        health_link = page.locator('a[href="/health"]')
        expect(health_link).to_be_visible()
        expect(health_link).to_contain_text("Health Check")

        # Click and navigate to health check
        health_link.click()
        expect(page).to_have_url(f"{get_base_url()}/health")
        
        # Go back to home page
        page.go_back()
        expect(page).to_have_url(f"{get_base_url()}/")
        
    finally:
        context.close()
        browser.close()