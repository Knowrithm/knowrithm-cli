import click
from click.testing import CliRunner
from knowrithm_cli.commands.agent import delete_agent, update_agent
from knowrithm_cli.commands.document import delete_document, agent_documents
from knowrithm_cli.commands.conversation import chat, messages
from knowrithm_cli.commands.database import get_connection
from knowrithm_cli.commands.company import get_company
from knowrithm_cli.commands.lead import get_lead

def test_optional_arguments():
    """Test that arguments are now optional for interactive commands."""
    
    # Helper to check if a command argument is required
    def is_arg_required(command, arg_name):
        for param in command.params:
            if param.name == arg_name:
                return param.required
        return None

    print("=== Verifying Command Arguments ===\n")

    # Check Agent commands
    print("1. Checking Agent commands...")
    assert is_arg_required(delete_agent, "agent_name_or_id") is False, "delete_agent argument should be optional"
    assert is_arg_required(update_agent, "agent_name_or_id") is False, "update_agent argument should be optional"
    print("   ✅ Agent commands verified")
    
    # Check Document commands
    print("2. Checking Document commands...")
    assert is_arg_required(delete_document, "document_id") is False, "delete_document argument should be optional"
    assert is_arg_required(agent_documents, "agent_id") is False, "agent_documents argument should be optional"
    print("   ✅ Document commands verified")
    
    # Check Conversation commands
    print("3. Checking Conversation commands...")
    assert is_arg_required(chat, "conversation_id") is False, "chat conversation_id should be optional"
    assert is_arg_required(messages, "conversation_id") is False, "messages conversation_id should be optional"
    print("   ✅ Conversation commands verified")
    
    # Check Database commands
    print("4. Checking Database commands...")
    assert is_arg_required(get_connection, "connection_id") is False, "get_connection argument should be optional"
    print("   ✅ Database commands verified")
    
    # Check Company commands
    print("5. Checking Company commands...")
    assert is_arg_required(get_company, "company_id") is False, "get_company argument should be optional"
    print("   ✅ Company commands verified")
    
    # Check Lead commands
    print("6. Checking Lead commands...")
    assert is_arg_required(get_lead, "lead_id") is False, "get_lead argument should be optional"
    print("   ✅ Lead commands verified")
    
    # Check Settings commands
    from knowrithm_cli.commands.settings import get_settings, list_company_settings
    print("7. Checking Settings commands...")
    assert is_arg_required(get_settings, "settings_id") is False, "get_settings argument should be optional"
    assert is_arg_required(list_company_settings, "company_id") is False, "list_company_settings argument should be optional"
    print("   ✅ Settings commands verified")
    
    # Check Website commands
    from knowrithm_cli.commands.website import get_source, agent_sources
    print("8. Checking Website commands...")
    assert is_arg_required(get_source, "source_id") is False, "get_source argument should be optional"
    assert is_arg_required(agent_sources, "agent_id_or_name") is False, "agent_sources argument should be optional"
    print("   ✅ Website commands verified")
    
    print("\n✅ All command arguments verified as optional!")

if __name__ == "__main__":
    try:
        test_optional_arguments()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
