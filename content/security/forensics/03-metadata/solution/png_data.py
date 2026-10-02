import base64

# A small but valid PNG carrying two tEXt metadata chunks - the kind of
# embedded information that quietly leaks who made a file and where.
SAMPLE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAD3RFWHRBdXRob3IASmFuZSBEb2U0ahlJAAAAIHRFWHRDb21tZW50AHRha2VuIGF0IDUxLjUwNzQsLTAuMTI3OPFxWOoAAAALSURBVHicY/iPBABNvwv11q9plQAAAABJRU5ErkJggg=="
)
