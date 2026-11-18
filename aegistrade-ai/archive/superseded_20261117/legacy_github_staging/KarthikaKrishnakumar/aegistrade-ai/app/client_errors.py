"""Small typed HTTP error adapter: show actionable API details without echoing inputs."""
import os


def clean(text):
    text=str(text)
    for name in ('OPENROUTER_API_KEY','AEGIS_REVIEWER_TOKEN','AEGIS_GRAFANA_PASSWORD'):
        secret=os.getenv(name,'')
        if secret:text=text.replace(secret,'[REDACTED]')
    return text[:2000]

class APIError(RuntimeError):
    def __init__(self,status,detail,action=None,code=None):
        self.status=status;self.detail=clean(detail);self.action=clean(action) if action else None;self.code=code
        super().__init__(f'API {status}: {self.detail}')

    @classmethod
    def from_response(cls,response):
        try:detail=response.json().get('detail',response.text)
        except (ValueError,AttributeError):detail=response.text
        action=code=None
        if isinstance(detail,dict):
            action=detail.get('action');code=detail.get('code');detail=detail.get('message') or str(detail)
        elif isinstance(detail,list):
            detail='; '.join('.'.join(str(p) for p in x.get('loc',[]))+': '+x.get('msg','Invalid value') for x in detail if isinstance(x,dict))
        return cls(response.status_code,detail or 'The API did not return an error explanation.',action,code)
