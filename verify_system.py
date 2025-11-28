#!/usr/bin/env python3
"""
MedAssist System Verification Script
Run this to verify all hackathon requirements are working correctly.
"""

import asyncio
import json
import sys
from typing import Dict, Any
import httpx


class SystemVerifier:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    async def verify_all(self) -> Dict[str, Any]:
        """Verify all system components."""
        print("🔍 Starting MedAssist System Verification...")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("Multi-Agent System", self.test_multi_agent),
            ("Tools Integration", self.test_tools),
            ("Long-running Operations", self.test_loop_agent),
            ("Observability", self.test_observability),
            ("Agent Evaluation", self.test_evaluation),
            ("A2A Protocol", self.test_a2a),
            ("System Test", self.test_system)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = await test_func()
                self.results[test_name] = {"status": "✅ PASS", "details": result}
                print(f"   ✅ {test_name}: PASSED")
            except Exception as e:
                self.results[test_name] = {"status": "❌ FAIL", "error": str(e)}
                print(f"   ❌ {test_name}: FAILED - {e}")
        
        return self.results
    
    async def test_health(self) -> Dict[str, Any]:
        """Test basic health endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
    
    async def test_multi_agent(self) -> Dict[str, Any]:
        """Test multi-agent system."""
        async with httpx.AsyncClient() as client:
            # Test LLM-powered triage agent
            triage_payload = {
                "user_id": "verify-test",
                "symptoms": "mild headache",
                "context": "verification test"
            }
            triage_response = await client.post(
                f"{self.base_url}/triage", 
                json=triage_payload,
                timeout=30.0
            )
            triage_response.raise_for_status()
            
            # Test parallel agent coordination
            parallel_payload = {
                "user_id": "verify-test",
                "symptoms": "headache",
                "medications": ["aspirin"],
                "context": "test"
            }
            parallel_response = await client.post(
                f"{self.base_url}/health-assessment",
                json=parallel_payload,
                timeout=30.0
            )
            parallel_response.raise_for_status()
            
            return {
                "triage": triage_response.json(),
                "parallel": parallel_response.json()
            }
    
    async def test_tools(self) -> Dict[str, Any]:
        """Test tools integration."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
    
    async def test_loop_agent(self) -> Dict[str, Any]:
        """Test long-running loop agent operations."""
        async with httpx.AsyncClient() as client:
            # Check status
            status_response = await client.get(f"{self.base_url}/reminders/status")
            status_response.raise_for_status()
            
            # Test pause
            pause_response = await client.post(f"{self.base_url}/reminders/pause")
            pause_response.raise_for_status()
            
            # Test resume
            resume_response = await client.post(f"{self.base_url}/reminders/resume")
            resume_response.raise_for_status()
            
            return {
                "status": status_response.json(),
                "pause": pause_response.json(),
                "resume": resume_response.json()
            }
    
    async def test_observability(self) -> Dict[str, Any]:
        """Test observability features."""
        async with httpx.AsyncClient() as client:
            # Test metrics
            metrics_response = await client.get(f"{self.base_url}/metrics")
            metrics_response.raise_for_status()
            
            # Test traces
            traces_response = await client.get(f"{self.base_url}/traces")
            traces_response.raise_for_status()
            
            return {
                "metrics": metrics_response.json(),
                "traces": traces_response.json()
            }
    
    async def test_evaluation(self) -> Dict[str, Any]:
        """Test agent evaluation."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/evaluate", timeout=60.0)
            response.raise_for_status()
            return response.json()
    
    async def test_a2a(self) -> Dict[str, Any]:
        """Test A2A protocol."""
        async with httpx.AsyncClient() as client:
            # Send A2A message
            message_payload = {
                "sender": "triage",
                "receiver": "medication",
                "type": "health_consultation",
                "payload": {"user_id": "test", "data": "verification"}
            }
            send_response = await client.post(
                f"{self.base_url}/a2a/send",
                json=message_payload
            )
            send_response.raise_for_status()
            
            # Get message history
            history_response = await client.get(f"{self.base_url}/a2a/history")
            history_response.raise_for_status()
            
            return {
                "send": send_response.json(),
                "history": history_response.json()
            }
    
    async def test_system(self) -> Dict[str, Any]:
        """Test overall system functionality."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/test", timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.results.values() if "✅" in result["status"])
        total = len(self.results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is ready for evaluation.")
        else:
            print("\n⚠️  Some tests failed. Check the details above.")
        
        print("\n📋 HACKATHON REQUIREMENTS STATUS:")
        requirements = [
            "Multi-Agent System",
            "Tools Integration", 
            "Long-running Operations",
            "Observability",
            "Agent Evaluation",
            "A2A Protocol"
        ]
        
        for req in requirements:
            status = "✅" if req in self.results and "✅" in self.results[req]["status"] else "❌"
            print(f"   {status} {req}")


async def main():
    """Main verification function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🔗 Testing MedAssist at: {base_url}")
    
    verifier = SystemVerifier(base_url)
    
    try:
        await verifier.verify_all()
        verifier.print_summary()
        
        # Save results to file
        with open("verification_results.json", "w") as f:
            json.dump(verifier.results, f, indent=2)
        print(f"\n💾 Results saved to: verification_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Verification interrupted by user")
    except Exception as e:
        print(f"\n💥 Verification failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())